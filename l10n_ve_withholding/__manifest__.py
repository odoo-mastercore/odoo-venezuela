# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'name': "Venezuela - Payment Withholding",
    'description': """
        **Localización VENEZUELA Withholding**

        ¡Felicidades!. Este es el módulo Withholding para la implementación de
        la **Localización Venezuela** que agrega características y datos
        necesarios para un correcto ejercicio fiscal de su empresa.
    """,
    'author': "SINAPSYS GLOBAL SA || MASTERCORE SAS",
    'website': "https://mastercore.us",
    'version': '0.1',
    'countries': ['ve'],
    'category': 'Accounting/Localizations',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'l10n_ve_base',
        'account_payment_pro'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/seniat_factor.xml',
        'data/seniat_partner_type.xml',
        'data/seniat_ut.xml',
        'data/seniat_tabla_islr.xml',
        # 'reports/report_templates.xml',
        'reports/report_withholding_certificate.xml',
        'reports/report_withholding_certificate_iva.xml',
        # 'reports/report_payment_group.xml',
        'views/res_company.xml',
        'views/account_payment_view.xml',
        'views/res_partner_view.xml',
        'views/account_journal_view.xml',
        'views/account_move_view.xml',
        'views/account_tax_views.xml',
        'views/seniat_ut_view.xml',
        'views/seniat_factor_view.xml',
        'views/seniat_partner_type_view.xml',
        'views/seniat_tabla_islr_view.xml',
        'views/product_template.xml',
        'views/l10n_ve_payment_withholding.xml',
        'views/res_config_settings.xml'
    ],
    'installable': True,
    'post_init_hook': '_l10n_ve_wth_post_init',
}
