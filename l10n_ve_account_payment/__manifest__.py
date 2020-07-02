###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'name': "Localización Payment Venezuela",
    'description': """
        **Localización VENEZUELA Payment**

        ¡Felicidades!. Este es el módulo Payment para la implementación de la
        **Localización Venezuela** que agrega características y datos necesarios
        para un correcto ejercicio fiscal de su empresa.
    """,

    'author': "SINAPSYS GLOBAL SA || MASTERCORE SAS",
    'website': "http://sinapsys.global",
    'version': '13.0.1',
    'category': 'Localization',
    'license': 'AGPL-3',
    'depends': ['account',],
    'data': [
        'security/account_debt_management_security.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'wizard/account_payment_group_invoice_wizard_view.xml',
        'wizard/res_config_settings_views.xml',
        'views/account_move_line_view.xml',
        'views/account_payment_group_view.xml',
        'views/account_journal_dashboard_view.xml',
        'views/report_payment_group.xml',
        'data/mail_template_data.xml',
    ],

}
