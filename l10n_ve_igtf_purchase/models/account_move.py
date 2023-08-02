# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    igtf_base_purchase = fields.Float('Igtf base')
    igtf_amount_purchase = fields.Float('Monto igtf')
    igtf_base_purchase_usd = fields.Float('Igtf base usd')
    igtf_amount_purchase_usd = fields.Float('Monto igtf usd')
    igtf_purchase_apply_purchase = fields.Boolean('Aplicar igtf')