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

        with patch.object(
            payment.__class__,
            "_l10n_ve_get_gross_payment_amount",
            autospec=True,
            return_value=207.64,
        ), patch.object(
            payment.__class__,
            "_l10n_ve_get_withholding_amount_in_payment_currency",
            autospec=True,
            return_value=12.02,
        ):
            payment._l10n_ve_adjust_foreign_payment_for_withholdings()

        self.assertAlmostEqual(payment.amount, 195.62, places=6)
        self.assertAlmostEqual(payment.amount_exact, 195.62, places=6)
