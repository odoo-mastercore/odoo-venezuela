# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class withholdingDistributionIslr(models.Model):
    _name = 'withholding.distribution.islr'
    _description = 'withholding distribution ISLR'

    payment_group_id = fields.Many2one(
        'account.payment.group', string='Pago')
    move_line_id = fields.Many2one(
        'account.move.line', 'Linea de factura',)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='move_line_id.currency_id'
    )
    price_subtotal = fields.Monetary(
        string='Subtotal',currency_field='currency_id',
        related='move_line_id.price_subtotal', store=True,
    )
    regimen_islr_id = fields.Many2one(
        'seniat.tabla.islr',
        'Aplicativo ISLR'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        related='move_line_id.product_id',
    )
    partner_regimen_islr_ids = fields.Many2many(
        'seniat.tabla.islr',
        related='payment_group_id.partner_regimen_islr_ids',
    )

