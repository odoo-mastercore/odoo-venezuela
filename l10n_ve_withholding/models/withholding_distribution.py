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

class withholdingDistribution(models.Model):
    _name = 'withholding.distribution'
    _description = 'withholding distribution'

    payment_id = fields.Many2one(
        'account.payment', string='Pago')
    invoice_amount = fields.Float('Base')
    tax_amount = fields.Float('Monto Impuesto')
    alic = fields.Float('alicuota')
    withholding_amount = fields.Float('Monto Retenido')
    untaxed_amount = fields.Float('Monto exento')

