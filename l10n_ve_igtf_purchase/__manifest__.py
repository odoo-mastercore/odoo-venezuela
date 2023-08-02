# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'name': "Localización Venezuela igtf compras",
    'description': """
        **Localización VENEZUELA igtf compras**
    """,

    'author': "SINAPSYS GLOBAL SA || MASTERCORE SAS",
    'website': "http://sinapsys.global",
    'version': '16.0.1',
    'category': 'Localization',
    'license': 'AGPL-3',
    'depends': ['account', 'l10n_ve_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_latam_identification_type_data.xml',
        'data/l10n_ve_responsibility_type_data.xml',
        'data/res_bank.xml',
        'data/account_tax_data.xml',
        'views/seniat_menuitem.xml',
        'views/l10n_ve_responsibility_type_view.xml',
        'views/res_partner_view.xml',
        'views/res_partner_bank_view.xml',
        'views/res_company_view.xml',
        'views/res_currency_view.xml',
        'wizard/currency_rate_wizard_view.xml'
    ],

}
