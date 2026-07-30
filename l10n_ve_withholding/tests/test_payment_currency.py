# -*- coding: utf-8 -*-
##############################################################################
# Author: Mastercore Sinapsys Global®
# Copyright: 2019-Present.
# License OPL-1 (Odoo Proprietary License v1.0)
# See https://www.odoo.com/documentation/master/legal/licenses.html
#
#
##############################################################################
from odoo import fields
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
