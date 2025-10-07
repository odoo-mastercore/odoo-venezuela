# -*- coding: utf-8 -*-
################################################################################
# Author: Mastercore Sinapsys Global®
# Copyright: 2019-Present.
# License OPL-1 (Odoo Proprietary License v1.0)
# See https://www.odoo.com/documentation/master/legal/licenses.html
#
################################################################################
{
    'name': "Base Validation Odoo Venezuela",
    'version': '18.0.0.1',
    'author': 'Mastercore Sinapsys Global®',
    'website': 'https://www.mastercore.us',
    'license': 'OPL-1',
    'category': 'Accounting',
    'summary': 'Base Validation Odoo Venezuela',
    'description': """
    """,
    'depends': ['account', 'base', 'product', 'sale', 'stock'],
    'data': [
            'views/account_tax_view.xml',
            'views/sale_order_view.xml',
            'views/account_move_view.xml',
            'views/stock_picking_view.xml',
        ],
    'installable': True,
    'auto_install': False,
}
