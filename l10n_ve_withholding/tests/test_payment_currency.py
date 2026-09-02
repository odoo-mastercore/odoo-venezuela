# -*- coding: utf-8 -*-
##############################################################################
# Author: Mastercore Sinapsys Global®
# Copyright: 2019-Present.
# License OPL-1 (Odoo Proprietary License v1.0)
# See https://www.odoo.com/documentation/master/legal/licenses.html
#
#
##############################################################################
from unittest.mock import patch

from odoo import Command, fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestPaymentCurrency(AccountTestInvoicingCommon):

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

    def test_foreign_payment_ignores_zero_withholding_suggestion(self):
        payment = self.env["account.payment"].new(
            {
                "company_id": self.env.company.id,
                "currency_id": self.currency_data["currency"].id,
                "payment_type": "inbound",
                "partner_type": "customer",
            }
        )
        withholding = self.env["l10n_ve.payment.withholding"].new(
            {
                "payment_id": payment,
                "tax_id": self.company_data["default_tax_sale"].id,
                "amount": 0.0,
            }
        )
        payment.l10n_ve_withholding_line_ids = withholding

        payment._check_withholdings_and_currency()

        withholding._update_cache({"amount": 1.0})
        with self.assertRaises(UserError):
            payment._check_withholdings_and_currency()

        payment._update_cache({"state": "canceled"})
        payment._check_withholdings_and_currency()

    def test_zero_withholding_does_not_change_payment_amount(self):
        payment = self.env["account.payment"].new(
            {
                "company_id": self.env.company.id,
                "currency_id": self.currency_data["currency"].id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "amount": 207.64,
                "amount_exact": 207.64,
            }
        )
        payment._update_cache(
            {
                "l10n_ve_withholdings_amount": 0.0,
                "payment_difference": -1322.42,
            }
        )

        payment._onchange_withholdings()

        self.assertEqual(payment.amount, 207.64)
        self.assertEqual(payment.amount_exact, 207.64)

    def test_foreign_withholding_reduces_payment_currency_amount(self):
        payment = self.env["account.payment"].new(
            {
                "company_id": self.env.company.id,
                "currency_id": self.currency_data["currency"].id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "amount": 207.64,
                "amount_exact": 207.64,
            }
        )
        payment._update_cache({"l10n_ve_withholdings_amount": 9000.0})
        withholding_amount = 9000.0 / 748.7864
        expected_amount_exact = 207.64 - withholding_amount

        with patch.object(
            payment.__class__,
            "_l10n_ve_get_gross_payment_amount",
            autospec=True,
            return_value=207.64,
        ), patch.object(
            payment.__class__,
            "_l10n_ve_get_withholding_amount_in_payment_currency",
            autospec=True,
            return_value=withholding_amount,
        ):
            payment._l10n_ve_adjust_foreign_payment_for_withholdings()

        self.assertAlmostEqual(payment.amount, 195.62, places=6)
        self.assertAlmostEqual(payment.amount_exact, expected_amount_exact, places=6)

    def test_company_currency_payment_withholding_uses_current_debt_value(self):
        invoice = self.init_invoice(
            "out_invoice",
            invoice_date=fields.Date.from_string("2017-01-01"),
            post=True,
            amounts=[600.0],
            currency=self.currency_data["currency"],
        )
        receivable_line = invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        payment = self.env["account.payment"].new(
            {
                "company_id": self.env.company.id,
                "currency_id": self.env.company.currency_id.id,
                "partner_id": invoice.partner_id.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "amount": 156800.43,
                "to_pay_move_line_ids": [Command.set(receivable_line.ids)],
            }
        )
        payment._update_cache({"l10n_ve_withholdings_amount": 9000.0})

        with patch.object(
            payment.__class__,
            "_l10n_ve_get_gross_payment_amount",
            autospec=True,
            return_value=156800.43,
        ), patch.object(
            payment.__class__,
            "_l10n_ve_get_withholding_amount_in_payment_currency",
            autospec=True,
            return_value=9000.0,
        ):
            payment._onchange_withholdings()

        self.assertEqual(payment.amount, 147800.43)
        self.assertFalse(payment.force_amount_company_currency)

    def test_islr_base_uses_invoice_accounting_amount(self):
        invoice = self.init_invoice(
            "in_invoice",
            invoice_date=fields.Date.from_string("2017-01-01"),
            post=True,
            amounts=[600.0],
            currency=self.currency_data["currency"],
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
        self.assertTrue(self.env.company.currency_id.is_zero(sum(move.line_ids.mapped("balance"))))
        self.assertTrue(withholding.exists())
        self.assertEqual(withholding.state, "posted")
        self.assertEqual(withholding.name, "TEST-WH-0001")

        payment.action_cancel()

        self.assertTrue(withholding.exists())
        self.assertEqual(withholding.state, "cancel")
        self.assertTrue(withholding.cancel_date)
