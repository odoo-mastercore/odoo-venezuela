# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
{
    'author': 'ADHOC SA, SINAPSYS GLOBAL SA || MASTERCORE SA',
    'website': 'www.sinapsys.global',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'data': [
        'wizards/res_config_settings_views.xml',
        'views/account_tax_view.xml',
        'views/account_payment_group_view.xml',
        'views/account_payment_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/withholding_demo.xml',
    ],
    'depends': [
        'l10n_ve_account_payment_group',
        'l10n_ve_account_withholding',
    ],
    'installable': True,
    'name': 'Automatic Withholdings on Payments',
    'test': [],
    'version': "13.0.1.0.0",
}
