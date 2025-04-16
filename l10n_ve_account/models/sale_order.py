# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging
import re
from datetime import datetime
_logger = logging.getLogger(__name__)


class saleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """
        Override the action_confirm method to set the invoice date
        when confirming a sale order.
        """
        res = super(saleOrder, self).action_confirm()
        for rec in self:
            for line in rec.order_line:
                if not line.order_line.tax_id:
                    raise ValidationError(
                        _("El producto %s no tiene impuestos asignados.") % line.product_id.display_name
                    )
        return res

