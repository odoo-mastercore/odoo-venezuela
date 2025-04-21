# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import formatLang
import json
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    igtf_base_purchase = fields.Float('IGTF base Bs.', copy=False)
    igtf_amount_purchase = fields.Float('Monto IGTF Bs.', copy=False)
    igtf_base_purchase_usd = fields.Float('IGTF base USD', copy=False)
    igtf_amount_purchase_usd = fields.Float('Monto IGTF USD',copy=False)
    igtf_purchase_apply_purchase = fields.Boolean('Aplicar IGTF',copy=False)
    
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_tax_totals_json(self):
        super(AccountMove, self)._compute_tax_totals_json()
        for move in self:
            if move.tax_totals_json:
                tax_total_json = json.loads(move.tax_totals_json)
                if tax_total_json and tax_total_json.get('groups_by_subtotal'):
                    base_imponible = tax_total_json.get('groups_by_subtotal').get('Base imponible')
                    if move.igtf_purchase_apply_purchase:
                        igtf = self.env['account.tax'].search([('igtf_purchase','=',True)], limit=1)
                        igtf_tax = False
                        
                        if move.currency_id.name != 'USD':
                            amount = move.igtf_amount_purchase
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
                            amount = move.igtf_amount_purchase_usd
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
                            tax_total_json['groups_by_subtotal']['Base imponible'] = base_imponible
                            tax_total_json['amount_total'] += amount
                            tax_total_json['formatted_amount_total'] = formatLang(self.env, tax_total_json['amount_total'], currency_obj=move.currency_id)
                            move.tax_totals_json = json.dumps(tax_total_json)

    
    
    @api.constrains('partner_id','igtf_purchase_apply_purchase','igtf_amount_purchase','igtf_amount_purchase_usd')
    def _constrains_igtf(self):
        for move in self:
            if move.igtf_purchase_apply_purchase and move.igtf_amount_purchase>=0:
                igtf = self.env['account.tax'].search([('igtf_purchase','=',True)], limit=1)
                account_id = self.env['account.tax.repartition.line'].search([('repartition_type','=','tax'),
                                                                            ('invoice_tax_id','=',igtf.id)])[0].account_id
                get_line_igtf = self.env['account.move.line'].search([('move_id','=', move._origin.id)]).mapped('igtf_purchase')
                is_igtf = False
                for rec in get_line_igtf:
                    if rec:
                        is_igtf = rec
                if move.currency_id.name != 'USD':
                    if not is_igtf and move.igtf_amount_purchase>=0:
                        move.line_ids  += self.env['account.move.line'].create({
                            # 'display_type':'tax',
                            'name': igtf.name,
                            'exclude_from_invoice_tab':True,
                            'partner_id': move.partner_id.id,
                            'account_id': account_id.id,
                            'igtf_purchase': True,
                            'currency_id': move.currency_id.id,
                            'debit': move.igtf_amount_purchase,
                            'tax_ids': [],
                            'move_id': move._origin.id,
                        })
                elif move.currency_id.name == 'USD':
                    if not is_igtf and move.igtf_amount_purchase_usd>=0:
                        move.line_ids  += move.env['account.move.line'].create({
                            # 'display_type':'tax',
                            'name': igtf.name,
                            'exclude_from_invoice_tab':True,
                            'partner_id': move.partner_id.id,
                            'account_id': account_id.id,
                            'igtf_purchase': True,
                            'currency_id': move.currency_id.id,
                            'debit':move.igtf_amount_purchase,
                            'tax_ids': [],
                            'move_id': move._origin.id
                        })
                invoice_line = move.invoice_line_ids.search([('name','ilike','IGTF 3%'),('move_id','=', move._origin.id)])
                if move.currency_id.name != 'USD':
                    invoice_line.sudo().write({'debit': move.igtf_amount_purchase})
                elif move.currency_id.name == 'USD':
                    invoice_line.sudo().write({'debit': move.igtf_amount_purchase})
        
    
    @api.constrains('igtf_purchase_apply_purchase')
    def _constrains_delete_igtf(self):
        invoice_line = self.line_ids.search([('igtf_purchase','=',True),('move_id','=', self._origin.id)])
        if not self.igtf_purchase_apply_purchase and invoice_line:
            invoice_line.unlink()