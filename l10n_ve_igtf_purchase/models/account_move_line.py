# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    igtf_purchase = fields.Boolean(string="Compra IGTF")


    @api.ondelete(at_uninstall=False)
    def _prevent_automatic_line_deletion(self):
        if not self.env.context.get('dynamic_unlink'):
            for line in self:
                if not line.igtf_purchase: 
                    if line.display_type == 'tax' and line.move_id.line_ids.tax_ids:
                        raise ValidationError(_(
                            "You cannot delete a tax line as it would impact the tax report"
                        ))
                    elif line.display_type == 'payment_term':
                        raise ValidationError(_(
                            "You cannot delete a payable/receivable line as it would not be consistent "
                            "with the payment terms"
                        ))
                if line.igtf_purchase and line.move_id.igtf_purchase_apply_purchase: 
                    if line.display_type == 'tax' and line.move_id.line_ids.tax_ids:
                        raise ValidationError(_(
                            "You cannot delete a tax line as it would impact the tax report"
                        ))
                    elif line.display_type == 'payment_term':
                        raise ValidationError(_(
                            "You cannot delete a payable/receivable line as it would not be consistent "
                            "with the payment terms"
                        ))
    