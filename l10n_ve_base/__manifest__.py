# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
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
    'version': '13.0.1',
    'category': 'Localization',
    'license': 'AGPL-3',
    'depends': ['base','contacts','l10n_ve','territorial_pd','l10n_latam_base'],
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
    ],

}
