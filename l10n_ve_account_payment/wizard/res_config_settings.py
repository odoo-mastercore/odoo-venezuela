###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_account_use_financial_amounts = fields.Boolean(
        "Use Financial Amounts",
        help='Display Financial amounts on partner debts views and reports.\n'
        'Financial amounts are amounts on other currency converted to company '
        'currency on todays exchange.',
        implied_group='l10n_ve_account_payment.account_use_financial_amounts')

    group_choose_payment_type = fields.Boolean(
        'Choose Payment Type on Payments',
        implied_group='l10n_ve_account_payment.group_choose_payment_type',
    )
    group_pay_now_customer_invoices = fields.Boolean(
        'Allow pay now on customer invoices?',
        implied_group='l10n_ve_account_payment.group_pay_now_customer_invoices',
    )
    group_pay_now_vendor_invoices = fields.Boolean(
        'Allow pay now on vendor invoices?',
        help='Allow users to choose a payment journal on invoices so that '
        'invoice is automatically paid after invoice validation. A payment '
        'will be created using choosen journal',
        implied_group='l10n_ve_account_payment.group_pay_now_vendor_invoices',
    )
    double_validation = fields.Boolean(
        related='company_id.double_validation',
        readonly=False,
    )
