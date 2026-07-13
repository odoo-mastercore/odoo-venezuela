# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api
from odoo.tools import formatLang


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
        'igtf_purchase_apply_purchase',
        'igtf_base_purchase',
        'igtf_amount_purchase',
        'igtf_base_purchase_usd',
        'igtf_amount_purchase_usd',
    )
    def _compute_tax_totals(self):
        super(AccountMove, self)._compute_tax_totals()
        for move in self:
            move._inject_igtf_purchase_tax_totals()

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

    def _inject_igtf_purchase_tax_totals(self):
        self.ensure_one()
        if not self.tax_totals or not self.is_invoice(include_receipts=True):
            return

        tax = self._get_igtf_purchase_tax()
        igtf_tax_values = self._get_igtf_purchase_tax_values()
        if not tax or not tax.tax_group_id or not igtf_tax_values:
            return

        tax_totals = dict(self.tax_totals)
        groups_by_subtotal = dict(tax_totals.get('groups_by_subtotal') or {})
        subtotal_name = next(
            (
                subtotal.get('name')
                for subtotal in tax_totals.get('subtotals', [])
                if subtotal.get('name') in groups_by_subtotal
            ),
            False,
        ) or next(iter(groups_by_subtotal), False)
        if not subtotal_name:
            return

        subtotal_groups = list(groups_by_subtotal.get(subtotal_name, []))
        amount = self.currency_id.round(abs(igtf_tax_values['amount_currency'] or igtf_tax_values['balance']))
        base_amount = self.currency_id.round(abs(
            self.igtf_base_purchase_usd
            if self.currency_id != self.company_currency_id
            else self.igtf_base_purchase
        ))

        igtf_group = {
            'group_key': tax.tax_group_id.id,
            'tax_group_id': tax.tax_group_id.id,
            'tax_group_name': tax.tax_group_id.name,
            'tax_group_amount': amount,
            'tax_group_base_amount': base_amount,
            'formatted_tax_group_amount': formatLang(self.env, amount, currency_obj=self.currency_id),
            'formatted_tax_group_base_amount': formatLang(self.env, base_amount, currency_obj=self.currency_id),
            'hide_base_amount': False,
        }

        existing_group = next(
            (
                group for group in subtotal_groups
                if group.get('tax_group_id') == tax.tax_group_id.id
            ),
            False,
        )
        existing_amount = existing_group.get('tax_group_amount', 0.0) if existing_group else 0.0
        if existing_group:
            existing_group.update(igtf_group)
        else:
            subtotal_groups.append(igtf_group)

        groups_by_subtotal[subtotal_name] = subtotal_groups
        tax_totals['groups_by_subtotal'] = groups_by_subtotal

        computed_total = (tax_totals.get('amount_total') or 0.0) + (amount - existing_amount)
        total_amount = self.currency_id.round(max(self.amount_total, computed_total))
        tax_totals['amount_total'] = total_amount
        tax_totals['formatted_amount_total'] = formatLang(self.env, total_amount, currency_obj=self.currency_id)
        self.tax_totals = tax_totals

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
