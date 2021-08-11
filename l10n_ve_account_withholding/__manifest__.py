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
        'views/account_tax_view.xml',
        'views/account_payment_view.xml',
        'data/account_payment_method_data.xml',
    ],
    'depends': [
        'account',
        # for payment method description and company_id field on form view
        'l10n_ve_account_payment_fix',
    ],
    'installable': True,
    'name': 'Withholdings on Payments',
    'test': [],
    'version': "13.0.1.0.0",
}
