# -*- coding: utf-8 -*-
##############################################################################
# Author: Mastercore Sinapsys Global®
# Copyright: 2019-Present.
# License OPL-1 (Odoo Proprietary License v1.0)
# See https://www.odoo.com/documentation/master/legal/licenses.html
#
#
##############################################################################
from odoo import Command, fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestPaymentCurrency(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.foreign_currency = cls.setup_other_currency("EUR")
        cls.foreign_journal = cls.env["account.journal"].create(
            {
                "name": "Banco Moneda Extranjera",
                "type": "bank",
                "code": "BME",
                "company_id": cls.env.company.id,
                "currency_id": cls.foreign_currency.id,
            }
        )

    def _new_foreign_currency_payment(self):
        payment = self.env["account.payment"].new(
            {
                "company_id": self.env.company.id,
                "journal_id": self.foreign_journal.id,
                "currency_id": self.foreign_currency.id,
                "counterpart_currency_id": self.env.company.currency_id.id,
                "payment_type": "outbound",
                "partner_type": "supplier",
                "date": fields.Date.today(),
                "amount": 100.0,
                "amount_exact": 100.0,
            }
        )
        payment._update_cache(
            {
                "destination_currency_id": self.env.company.currency_id.id,
            }
        )
        return payment

    def _create_customer_payment_with_numbered_withholding(self):
        self.env.company.use_payment_pro = True
        journal = self.company_data["default_journal_bank"]
        journal.currency_id = False
        withholding_tax = self.company_data["default_tax_sale"].copy(
            {
                "name": "Customer payment withholding",
                "type_tax_use": "none",
                "l10n_ve_tax_type": "partner_tax",
                "l10n_ve_withholding_payment_type": "customer",
            }
        )
        tax_repartition_lines = (
            withholding_tax.invoice_repartition_line_ids
            | withholding_tax.refund_repartition_line_ids
        ).filtered(lambda line: line.repartition_type == "tax")
        tax_repartition_lines.account_id = self.company_data["default_account_revenue"]
        payment = self.env["account.payment"].create(
            {
                "company_id": self.env.company.id,
                "partner_id": self.partner_a.id,
                "partner_type": "customer",
                "payment_type": "inbound",
                "journal_id": journal.id,
                "currency_id": self.env.company.currency_id.id,
                "amount": 900.0,
            }
        )
        withholding = self.env["l10n_ve.payment.withholding"].create(
            {
                "payment_id": payment.id,
                "tax_id": withholding_tax.id,
                "name": "TEST-WH-0001",
                "base_amount": 1000.0,
                "amount": 100.0,
            }
        )
        return payment, withholding

    def test_zero_withholding_does_not_change_payment_amount(self):
        payment = self._new_foreign_currency_payment()
        payment._update_cache(
            {
                "l10n_ve_withholdings_amount": 0.0,
                "payment_difference": 500.0,
            }
        )

        payment._onchange_withholdings()

        self.assertEqual(payment.amount, 100.0)
        self.assertEqual(payment.amount_exact, 100.0)

    def test_withholding_difference_is_converted_to_payment_currency(self):
        payment = self._new_foreign_currency_payment()
        payment._update_cache(
            {
                "l10n_ve_withholdings_amount": 50.0,
                "payment_difference": -50.0,
            }
        )
        expected_amount = payment.amount_exact + payment._get_payment_difference_in_currency_a()

        payment._onchange_withholdings()

        self.assertAlmostEqual(payment.amount, expected_amount, places=6)
        self.assertAlmostEqual(payment.amount_exact, expected_amount, places=6)

    def test_withholding_move_rate_uses_payment_accounting_rate(self):
        payment = self._new_foreign_currency_payment()
        payment._update_cache(
            {
                "accounting_rate": 1.0 / 744.2264,
                "to_pay_move_line_ids": False,
            }
        )

        currency_data = payment._get_withholding_move_currency_data()

        self.assertEqual(currency_data["currency"], self.foreign_currency)
        self.assertAlmostEqual(
            currency_data["conversion_rate"],
            744.2264,
            places=4,
        )

    def test_withholding_move_uses_company_journal_currency(self):
        company_currency = self.env.company.currency_id
        payment = self.env["account.payment"].new(
            {
                "company_id": self.env.company.id,
                "journal_id": self.company_data["default_journal_bank"].id,
                "currency_id": company_currency.id,
                "payment_type": "outbound",
                "partner_type": "supplier",
                "date": fields.Date.today(),
                "amount": 10_000.0,
                "amount_exact": 10_000.0,
            }
        )

        currency_data = payment._get_withholding_move_currency_data()

        self.assertEqual(currency_data["currency"], company_currency)
        self.assertEqual(currency_data["conversion_rate"], 1.0)

    def test_canceled_withholding_is_not_effective(self):
        payment = self._new_foreign_currency_payment()
        withholding = self.env["l10n_ve.payment.withholding"].new(
            {
                "payment_id": payment,
                "tax_id": self.company_data["default_tax_sale"].id,
                "state": "cancel",
                "amount": 100.0,
            }
        )
        payment.l10n_ve_withholding_line_ids = withholding

        self.assertFalse(payment._get_l10n_ve_effective_withholding_lines())
        payment._check_withholdings_and_currency()

    def test_canceled_withholding_allows_automatic_regeneration(self):
        invoice = self.init_invoice(
            "in_invoice",
            invoice_date=fields.Date.from_string("2017-01-01"),
            post=True,
            amounts=[600.0],
        )
        payable_line = invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        )
        withholding_tax = self.company_data["default_tax_purchase"]
        canceled_withholding = self.env["l10n_ve.payment.withholding"].create(
            {
                "tax_id": withholding_tax.id,
                "name": "TEST-CANCELED-AUTO",
                "state": "cancel",
                "amount": 100.0,
            }
        )
        invoice.l10n_ve_withholding_ids = [Command.link(canceled_withholding.id)]
        payment = self.env["account.payment"].new(
            {
                "company_id": self.env.company.id,
                "partner_id": invoice.partner_id.id,
                "partner_type": "supplier",
                "payment_type": "outbound",
                "to_pay_move_line_ids": [Command.set(payable_line.ids)],
            }
        )

        self.assertTrue(
            payment._has_l10n_ve_moves_without_withholding_tax(withholding_tax)
        )

    def test_islr_base_uses_invoice_accounting_amount(self):
        invoice = self.init_invoice(
            "in_invoice",
            invoice_date=fields.Date.from_string("2017-01-01"),
            post=True,
            amounts=[600.0],
            currency=self.foreign_currency,
        )
        payable_line = invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        )
        payment = self.env["account.payment"].new(
            {
                "company_id": self.env.company.id,
                "partner_id": invoice.partner_id.id,
                "partner_type": "supplier",
                "payment_type": "outbound",
                "date": fields.Date.from_string("2019-01-01"),
                "to_pay_move_line_ids": [Command.set(payable_line.ids)],
            }
        )

        payment._compute_l10n_ve_withholding_untaxed()

        self.assertEqual(
            payment.l10n_ve_withholding_untaxed,
            abs(invoice.amount_untaxed_signed),
        )

    def test_numbered_withholding_survives_payment_reset_and_cancel(self):
        payment, withholding = self._create_customer_payment_with_numbered_withholding()
        payment.action_post()

        move = payment.move_id
        original_line_ids = move.line_ids.ids
        withholding_move_line = move.line_ids.filtered(
            lambda line: line.l10n_ve_withholding_line_id == withholding
        )
        self.assertTrue(withholding_move_line)
        self.assertTrue(payment._needs_withholding_draft_bypass())

        payment.action_draft()

        self.assertEqual(payment.state, "draft")
        self.assertEqual(move.state, "draft")
        self.assertEqual(move.line_ids.ids, original_line_ids)
        self.assertTrue(
            self.env.company.currency_id.is_zero(sum(move.line_ids.mapped("balance")))
        )
        self.assertTrue(withholding.exists())
        self.assertEqual(withholding.state, "posted")

        payment.action_cancel()

        self.assertEqual(withholding.state, "cancel")
        self.assertTrue(withholding.cancel_date)

    def test_numbered_withholding_survives_payment_unlink(self):
        payment, withholding = self._create_customer_payment_with_numbered_withholding()
        payment_name = payment.name or payment.move_id.name

        payment.unlink()

        self.assertTrue(withholding.exists())
        self.assertFalse(withholding.payment_id)
        self.assertEqual(withholding.payment_name, payment_name)
        self.assertEqual(withholding.state, "cancel")
