# -*- coding: utf-8 -*-
################################################################################
# Author      : SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyright(c): 2021-Present.
# License URL : AGPL-3
################################################################################

{
    'name': 'Comprobantes para Factura Venezolana',
    'version': '15.0.0.1',
    'description': """
    **Comprobantes para Factura Venezolana**
    ¡Felicidades!. Este es el módulo para Generar Comprobantes PDF de
    Factura Venezolana para la implementación de la **Localización Venezolana**
    """,
    'author': 'SINAPSYS GLOBAL SA || MASTERCORE SAS',
    'website': 'www.sinapsys.global',
    'license': 'AGPL-3',
    'category': 'Localization / Venezuela',
    'depends': [
        'base',
        'account',
        'l10n_ve_base',
        'l10n_ve_withholding',
    ],
    'data': [
        'templates/report_invoice_ve.xml',
        'data/external_layout_report.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
