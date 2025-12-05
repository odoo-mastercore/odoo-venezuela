# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ve_invoice_date = fields.Datetime(
        string='Fecha y hora de la factura',
        readonly=True,
        copy=False,
    )

    def _post(self, soft=True):
        posted_moves = super()._post(soft=soft)
        for rec in posted_moves:
            # Se valida que no exista fecha de factura y se la asignamos
            # Con esto prevenimos que al validar facturas desde tome una fecha
            # Que no corresponda con el correlativo de la factura
            if rec.state == 'posted' and not rec.l10n_ve_invoice_date:
                rec.l10n_ve_invoice_date = fields.Datetime.now()
        return posted_moves

    def _get_l10n_ve_invoice_date(self, split=False):
        date, time = False, False
        if self.l10n_ve_invoice_date:
            date_tz = fields.Datetime.context_timestamp(self, self.l10n_ve_invoice_date)
            date = date_tz.strftime("%d-%m-%Y")
            time = date_tz.strftime("%H:%M:%S")
        if split:
            return (date, time)
        return f"{date} {time}" if date else False

    def _check_lines_price(self):
        FORBIDDEN_PATTER = r'\b(descuento|desc|des|discount)\b'
        """
          Para descuentos en líneas de factura, se permite el precio cero o negativo,
          dejamos el comodin de 'skip_check_price' para que no se valide el precio
          en caso de que se necesite validar el precio en otro momento.
        """
        if 'skip_check_price' in self._context:
            return True
        for line in self.invoice_line_ids.filtered(lambda x: x.product_id):
            if line.price_unit <= 0 and\
                self.move_type in ['out_invoice'] and not\
                re.search(FORBIDDEN_PATTER, line.product_id.name or '', re.IGNORECASE):
                raise ValidationError(
                    _("No se permiten precios cero o negativos en las líneas de factura. Línea con producto: %s")
                    % line.product_id.display_name
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AccountMove, self).create(vals_list)
        for rec in records:
            rec._check_lines_price()
        return records

    def write(self, vals):
        rec = super(AccountMove, self).write(vals)
        if any(field in vals for field in ('line_ids', 'invoice_line_ids')):
            self._check_lines_price()
        return rec

    def _compute_tax_totals(self):
        """
        Hereda y ajusta la estructura de tax_totals:
        - Solo items con impuestos > 0 en base imponible normal.
        - Agrega sección 'Exento' para base imponible de impuestos con monto 0.
        """
        for move in self:
            if move.is_invoice(include_receipts=True):
                base_lines, _tax_lines = move._get_rounded_base_and_tax_lines()
                base_lines_impuesto = []
                base_lines_exento = []
                for bl in base_lines:
                    tiene_impuesto = any(td['tax'].amount > 0 for td in bl.get('tax_details', {}).get('taxes_data', []))
                    tiene_exento = any(td['tax'].amount == 0 for td in bl.get('tax_details', {}).get('taxes_data', []))
                    if tiene_impuesto:
                        base_lines_impuesto.append(bl)
                    elif tiene_exento or not bl.get('tax_details', {}).get('taxes_data', []):
                        base_lines_exento.append(bl)
                tax_totals = self.env['account.tax']._get_tax_totals_summary(
                    base_lines=base_lines_impuesto,
                    currency=move.currency_id,
                    company=move.company_id,
                    cash_rounding=move.invoice_cash_rounding_id,
                )
                if base_lines_exento:
                    exento_totals = self.env['account.tax']._get_tax_totals_summary(
                        base_lines=base_lines_exento,
                        currency=move.currency_id,
                        company=move.company_id,
                        cash_rounding=None,
                    )
                    exento_subtotal = {
                        'name': _('Exento'),
                        'base_amount_currency': exento_totals['base_amount_currency'],
                        'base_amount': exento_totals['base_amount'],
                        'tax_amount_currency': 0.0,
                        'tax_amount': 0.0,
                        'tax_groups': [],
                    }
                    tax_totals['base_amount_currency'] += exento_totals['base_amount_currency']
                    tax_totals['base_amount'] += exento_totals['base_amount']
                    tax_totals['total_amount_currency'] += exento_totals['base_amount_currency']
                    tax_totals['total_amount'] += exento_totals['base_amount']
                    tax_totals['subtotals'] = [exento_subtotal] + tax_totals['subtotals']
                tax_totals['display_in_company_currency'] = (
                    move.company_id.display_invoice_tax_company_currency
                    and move.company_currency_id != move.currency_id
                    and tax_totals['has_tax_groups']
                    and move.is_sale_document(include_receipts=True)
                )
                move.tax_totals = tax_totals
            else:
                move.tax_totals = None
