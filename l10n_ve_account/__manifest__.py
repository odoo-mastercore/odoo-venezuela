# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'name': "Venezuelan Accounting",
    'description': "",
    'author': "SINAPSYS GLOBAL SA || MASTERCORE SAS",
    'website': "http://sinapsys.global",
    'version': '0.1',
    'category': 'Localization',
    'countries': ['ve'],
    'license': 'AGPL-3',
    'depends': [
        'base',
        'contacts',
        'l10n_ve_base'
    ],
    'data': [
        'views/account_move.xml'
    ]
}