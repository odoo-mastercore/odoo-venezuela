# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'name': "Localización Venezuela Base",
    'description': """
        **Localización VENEZUELA Base**

        ¡Felicidades!. Este es el módulo Base para la implementación de la
        **Localización Venezuela** que agrega características y datos necesarios
        para un correcto ejercicio fiscal de su empresa.

        Este módulo extiende algunos modelos base de Odoo relacionados a Datos de
        la Compañia/Configuración, Clientes y Proveedores; Datos de la División
        Politico Territorial; Datos de Cuenta Bancaria y Moneda.
        Adicionalmente se registran datos de localización relacionados con otros
        Modelos.
    """,

    'author': "SINAPSYS GLOBAL SA || MASTERCORE SAS",
    'website': "http://sinapsys.global",
    'version': '0.1',
    'category': 'Accounting/Localizations/Account Charts',
    'countries': ['ve'],
    'license': 'AGPL-3',
    'depends': [
        'base',
        'contacts',
        'account',
        # 'l10n_ve',
        'l10n_latam_base'
    ],
    'auto_install': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_latam_identification_type_data.xml',
        'data/l10n_ve_responsibility_type_data.xml',
        'data/res_bank.xml',
        # 'data/account_tax_data.xml',
        'data/res.country.state.csv',
        'data/res.country.state.municipality.csv',
        'data/res.country.state.municipality.parish.csv',
        'views/seniat_menuitem.xml',
        'views/l10n_ve_responsibility_type_view.xml',
        'views/res_partner_view.xml',
        'views/res_partner_bank_view.xml',
        'views/res_company_view.xml',
        'views/res_currency_view.xml',
        'views/res_country_state_municipality.xml',
        'views/res_country_state_municipality_parish.xml',
        'views/res_config_settings_view.xml',
        'wizard/currency_rate_wizard_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'l10n_ve_base/static/src/scss/style.scss'
        ]
    },
    'installable': True,
}
