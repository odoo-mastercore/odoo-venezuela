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
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestPaymentCurrency(AccountTestInvoicingCommon):

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
