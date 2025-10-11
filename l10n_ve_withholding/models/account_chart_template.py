# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('ve_base', 'account.account')
    def _get_ve_base_withholding_account_account(self):
        return self._parse_csv('ve_base', 'account.account', module='l10n_ve_withholding')

    @template('ve_base', 'account.tax.group')
    def _get_ve_base_withholding_account_tax_group(self):
        return self._parse_csv('ve_base', 'account.tax.group', module='l10n_ve_withholding')

    @template('ve_base', 'account.tax')
    def _get_ve_base_withholding_account_tax(self):
        return self._parse_csv('ve_base', 'account.tax', module='l10n_ve_withholding')

    @template('ve_base', 'res.company')
    def _get_ve_base_res_company(self):
        res = super()._get_ve_base_res_company()
        res[self.env.company.id].update({'l10n_ve_tax_base_account_id': 'base_tax_account'})
        return res