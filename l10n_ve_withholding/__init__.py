# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from . import models
from . import wizard

def _l10n_ve_wth_post_init(env):
    """ Existing companies that have the Venezuela Chart of Accounts set """
    template_codes = ['ve_base']
    ar_companies = env['res.company'].search([('chart_template', 'in', template_codes), ('parent_id', '=', False)])
    for company in ar_companies:
        template_code = company.chart_template
        ChartTemplate = env['account.chart.template'].with_company(company)
        data = {
            model: ChartTemplate._parse_csv(template_code, model, module='l10n_ve_withholding')
            for model in [
                'account.account',
                'account.tax.group',
                'account.tax',
            ]
        }
        ChartTemplate._deref_account_tags(template_code, data['account.account'])
        ChartTemplate._deref_account_tags(template_code, data['account.tax.group'])
        ChartTemplate._deref_account_tags(template_code, data['account.tax'])
        ChartTemplate._pre_reload_data(company, {}, data)
        ChartTemplate._load_data(data)
        # company.l10n_ve_tax_base_account_id = ChartTemplate.ref('base_tax_account')