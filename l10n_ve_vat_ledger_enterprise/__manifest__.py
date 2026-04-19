# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2026-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'name': 'Venezuela VAT Ledger Enterprise',
    'summary': 'Libro IVA dinámico para Venezuela sobre account.report',
    'description': """
        Módulo Enterprise para los libros IVA de Venezuela.
        Agrega reportes dinámicos de compras y ventas usando account.report.
    """,
    'author': 'SINAPSYS GLOBAL SA || MASTERCORE SAS',
    'website': 'http://sinapsys.global',
    'version': '18.0.0.1',
    'countries': ['ve'],
    'category': 'Accounting/Localizations',
    'license': 'AGPL-3',
    'depends': [
        'l10n_ve_vat_ledger',
        'account_reports',
    ],
    'data': [
        'data/l10n_ve_vat_account_report.xml',
        'data/l10n_ve_vat_account_report_actions.xml',
    ],
    'installable': True,
}
