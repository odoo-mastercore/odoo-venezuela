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
from odoo.tools import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    igtf_base_purchase = fields.Float('IGTF base')
    igtf_amount_purchase = fields.Float('Monto IGTF')
    igtf_base_purchase_usd = fields.Float('IGTF base usd')
    igtf_amount_purchase_usd = fields.Float('Monto IGTF usd')
    igtf_purchase_apply_purchase = fields.Boolean('Aplicar IGTF')
    
    @api.depends_context('lang')
    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
        'igtf_purchase_apply_purchase'
    )
    def _compute_tax_totals(self):
        super(AccountMove, self)._compute_tax_totals()
        for move in self:
            if move.tax_totals and move.tax_totals.get('groups_by_subtotal'):
                base_imponible = move.tax_totals.get('groups_by_subtotal').get('Base imponible')
                if move.igtf_purchase_apply_purchase:
                    igtf = self.env['account.tax'].search([('name','=','IGTF (3.0%) compras')])
                    igtf_tax = False
                    
                    if move.currency_id.name != 'USD':
                        igtf_tax = {
                            'group_key': igtf.tax_group_id.id, 
                            'tax_group_id': igtf.tax_group_id.id, 
                            'tax_group_name': igtf.tax_group_id.name, 
                            'tax_group_amount': move.igtf_amount_purchase, 
                            'tax_group_base_amount': move.igtf_base_purchase, 
                            'formatted_tax_group_amount': formatLang(self.env,  move.igtf_amount_purchase , currency_obj=move.currency_id), 
                            'formatted_tax_group_base_amount': formatLang(self.env, move.igtf_base_purchase, currency_obj=move.currency_id)
                        }
                    elif move.currency_id.name == 'USD':
                        igtf_tax = {
                            'group_key': igtf.tax_group_id.id, 
                            'tax_group_id': igtf.tax_group_id.id, 
                            'tax_group_name': igtf.tax_group_id.name, 
                            'tax_group_amount': move.igtf_amount_purchase_usd, 
                            'tax_group_base_amount': move.igtf_base_purchase_usd,
                            'formatted_tax_group_amount': formatLang(self.env, move.igtf_amount_purchase_usd , currency_obj=move.currency_id),
                            'formatted_tax_group_base_amount': formatLang(self.env, move.igtf_base_purchase_usd, currency_obj=move.currency_id)
                        }
                    
                    if igtf_tax:

                        base_imponible.append(igtf_tax)
    