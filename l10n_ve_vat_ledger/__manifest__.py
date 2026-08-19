###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'name': "Localización Vat Ledger Venezuela",
    'description': """
        **Localización VENEZUELA Withholding**

        ¡Felicidades!. Este es el módulo Withholding para la implementación de 
        la **Localización Venezuela** que agrega características y datos 
        necesarios para la generacion de los libros Iva ventas/ Compras.
    """,

    'author': "SINAPSYS GLOBAL SA || MASTERCORE SAS",
    'website': "http://sinapsys.global",
    'version': '18.0.0.3',
    'countries': ['ve'],
    'category': 'Accounting/Localizations',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'l10n_ve_account',
        'l10n_ve_base',
        'l10n_ve_withholding',
        'report_xlsx',
        ],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_vat_ledger.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_view.xml',
        'report/account_vat_ledger_report.xml',
    ],

}