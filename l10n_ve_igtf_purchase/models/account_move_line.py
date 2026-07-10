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
from odoo.tools import frozendict

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    igtf_purchase = fields.Boolean(string="Compra IGTF")

    @api.depends(
        'tax_ids',
        'currency_id',
        'partner_id',
        'analytic_distribution',
        'balance',
        'move_id.partner_id',
        'price_unit',
        'quantity',
        'move_id.igtf_purchase_apply_purchase',
        'move_id.igtf_base_purchase',
        'move_id.igtf_amount_purchase',
        'move_id.igtf_base_purchase_usd',
        'move_id.igtf_amount_purchase_usd',
    )
    def _compute_all_tax(self):
        super()._compute_all_tax()
        for line in self.filtered(lambda line: line.display_type == 'product' and line.move_id.is_invoice(True)):
            move = line.move_id
            anchor_line = move.invoice_line_ids.filtered(lambda invoice_line: invoice_line.display_type == 'product')[:1]
            if line != anchor_line:
                continue

            igtf_tax_values = move._get_igtf_purchase_tax_values()
            if not igtf_tax_values:
                continue

            line.compute_all_tax_dirty = True
            line.compute_all_tax[frozendict({
                'tax_repartition_line_id': igtf_tax_values['tax_repartition_line_id'],
                'group_tax_id': False,
                'account_id': igtf_tax_values['account_id'],
                'currency_id': move.currency_id.id,
                'analytic_distribution': line.analytic_distribution if move.state == 'draft' else False,
                'tax_ids': [(6, 0, [igtf_tax_values['tax_id']])],
                'tax_tag_ids': [(6, 0, igtf_tax_values['tax_tag_ids'])],
                'partner_id': move.partner_id.id or line.partner_id.id,
                'move_id': move.id,
                'display_type': 'tax',
            })] = {
                'name': igtf_tax_values['name'],
                'balance': igtf_tax_values['balance'],
                'amount_currency': igtf_tax_values['amount_currency'],
                'tax_base_amount': igtf_tax_values['tax_base_amount'],
            }

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
    
