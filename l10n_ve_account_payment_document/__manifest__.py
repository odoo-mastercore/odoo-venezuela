###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'name': "Localización Payment Document Venezuela",
    'description': """
        **Localización VENEZUELA Payment Document**

        ¡Felicidades!. Este es el módulo Payment Document para la implementación de la
        **Localización Venezuela** que agrega características y datos necesarios
        para un correcto ejercicio fiscal de su empresa.
    """,

    'author': "SINAPSYS GLOBAL SA || MASTERCORE SAS",
    'website': "http://sinapsys.global",
    'version': '13.0.1',
    'category': 'Localization',
    'license': 'AGPL-3',
    'depends': [
        'l10n_latam_invoice_document',
        'l10n_ve_account_payment',
    ],
    'data': [
        'views/account_payment_group_view.xml',
        'views/account_payment_receiptbook_view.xml',
        'wizards/account_payment_group_invoice_wizard_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/decimal_precision_data.xml',
        'data/l10n_latam.document.type.csv',
        'reports/report_payment_group.xml',
    ],
    'demo': [
    ],
    'images': [
    ],
    'installable': True,
    'auto_install': True,
}
