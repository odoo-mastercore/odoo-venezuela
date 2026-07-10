# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    igtf_base_purchase = fields.Float('IGTF base Bs.', copy=False)
    igtf_amount_purchase = fields.Float('Monto IGTF Bs.',copy=False)
    igtf_base_purchase_usd = fields.Float('IGTF base USD',copy=False)
    igtf_amount_purchase_usd = fields.Float('Monto IGTF USD',copy=False)
    igtf_purchase_apply_purchase = fields.Boolean('Aplicar IGTF',copy=False)
    
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

    def _get_igtf_purchase_tax(self):
        self.ensure_one()
        return self.env['account.tax'].search([
            ('igtf_purchase', '=', True),
            ('company_id', '=', self.company_id.id),
        ], limit=1)

    def _get_igtf_purchase_tax_values(self):
        self.ensure_one()
        if not self.igtf_purchase_apply_purchase:
            return False

        tax = self._get_igtf_purchase_tax()
        repartition_line = tax.invoice_repartition_line_ids.filtered(
            lambda line: line.repartition_type == 'tax'
        )[:1]
        if not tax or not repartition_line:
            return False

        if self.currency_id != self.company_currency_id:
            amount_currency = self.igtf_amount_purchase_usd
            balance = self.igtf_amount_purchase
            tax_base_amount = self.igtf_base_purchase
        else:
            amount_currency = self.igtf_amount_purchase
            balance = self.igtf_amount_purchase
            tax_base_amount = self.igtf_base_purchase

        if not amount_currency and not balance:
            return False

        return {
            'account_id': repartition_line.account_id.id,
            'amount_currency': amount_currency,
            'balance': balance,
            'name': tax.name,
            'tax_base_amount': tax_base_amount,
            'tax_id': tax.id,
            'tax_repartition_line_id': repartition_line.id,
            'tax_tag_ids': repartition_line.tag_ids.ids,
        }

    def _cleanup_legacy_igtf_purchase_lines(self):
        legacy_lines = self.line_ids.filtered(
            lambda line: line.display_type == 'tax'
            and getattr(line, 'igtf_purchase', False)
            and not line.tax_line_id
        )
        if legacy_lines:
            legacy_lines.with_context(dynamic_unlink=True).unlink()

    def _sync_igtf_purchase_dynamic_lines(self):
        self.filtered(lambda move: move.state == 'draft')._cleanup_legacy_igtf_purchase_lines()

    @api.constrains(
        'partner_id',
        'igtf_purchase_apply_purchase',
        'igtf_base_purchase',
        'igtf_amount_purchase',
        'igtf_base_purchase_usd',
        'igtf_amount_purchase_usd',
    )
    def _constrains_igtf(self):
        self._sync_igtf_purchase_dynamic_lines()
