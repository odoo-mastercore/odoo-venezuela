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

    @template('ve_base', 'account.tax.group')
    def _get_ve_base_withholding_account_tax_group(self):
        return self._parse_csv('ve_base', 'account.tax.group', module='l10n_ve_withholding')

    @template('ve_base', 'account.tax')
    def _get_ve_base_withholding_account_tax(self):
        return self._parse_csv('ve_base', 'account.tax', module='l10n_ve_withholding')