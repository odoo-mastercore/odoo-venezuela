# -*- coding: utf-8 -*-
##############################################################################
# Author: Mastercore Sinapsys Global®
# Copyright: 2019-Present.
# License OPL-1 (Odoo Proprietary License v1.0)
# See https://www.odoo.com/documentation/master/legal/licenses.html
#
#
##############################################################################
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
