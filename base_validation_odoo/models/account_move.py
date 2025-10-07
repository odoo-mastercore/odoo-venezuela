# -*- coding: utf-8 -*-
################################################################################
# Author: Mastercore Sinapsys Global®
# Copyright: 2019-Present.
# License OPL-1 (Odoo Proprietary License v1.0)
# See https://www.odoo.com/documentation/master/legal/licenses.html
#
################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    print_count = fields.Integer(string='Número de Impresiones', default=0, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        _logger.warning('vals_list: %s', vals_list)
        for vals in vals_list:
            if (vals['move_type'] == 'out_invoice' or vals['move_type'] == 'in_invoice'):
                date_order = datetime.today()
                if (('invoice_date' in vals and vals['invoice_date'] == False) or 'invoice_date' not in vals):
                    vals['invoice_date'] = str(date_order)[0:10]
                if ('invoice_date_due' not in vals):
                    vals['invoice_date_due'] = str(date_order)[0:10]
                if (str(date_order)[0:10] > str(vals['invoice_date'])[0:10]):
                    raise ValidationError('La fecha de factura no puede ser inferior a la fecha actual.')
                if (str(date_order)[0:10] < str(vals['invoice_date'])[0:10]):
                    raise ValidationError('La fecha de factura no puede ser mayor a la fecha actual.')
                if (str(vals['invoice_date_due'])[0:10] < str(vals['invoice_date'])[0:10]):
                    raise ValidationError('La fecha de vencimiento no puede ser menor a la fecha de factura.')
                if (('invoice_line_ids' in vals and len(vals['invoice_line_ids']) == 0) or 'invoice_line_ids' not in vals):
                    raise ValidationError(_('No puede guardar facturas sin lineas asociadas.'))
                validate_product = False
                for line in vals['invoice_line_ids']:
                    if (line[2]['product_id'] != False):
                        validate_product = True
                    if (line[2]['product_id'] != False and len(line[2]['tax_ids']) == 0):
                        raise ValidationError(_('Las lineas de factura deben presentar un impuesto asignado.'))
                    if (line[2]['product_id'] != False and len(line[2]['tax_ids']) > 1):
                        raise ValidationError(_('Las lineas de factura no puede tener mas de un impuesto asignado.'))
                    if (line[2]['product_id'] != False and line[2]['price_unit'] == 0):
                        raise ValidationError(_('Las lineas de factura no pueden presentar precio unitario en 0.0.'))
                    if (line[2]['product_id'] != False and line[2]['price_unit'] < 0):
                        raise ValidationError(_('Las lineas de factura no pueden presentar precio unitario en negativo.'))
                    if (line[2]['product_id'] != False and line[2]['quantity'] == 0):
                        raise ValidationError(_('Las lineas de factura no pueden presentar cantidades en 0.0.'))
                    if (line[2]['product_id'] != False and line[2]['quantity'] < 0):
                        raise ValidationError(_('Las lineas de factura no pueden presentar cantidades en negativo.'))
                if (validate_product == False):
                    raise ValidationError(_('Las lineas de factura no presentan productos validos.'))
        res = super().create(vals_list)
        return res

    def _post(self, soft=True):
        for rec in self:
            if (rec.move_type in ['out_invoice', 'in_invoice']):
                invoice_date = datetime.today()
                if (str(invoice_date)[0:10] > str(rec.invoice_date)[0:10]):
                    raise ValidationError('La fecha de factura no puede ser inferior a la fecha actual.')
                if (str(invoice_date)[0:10] < str(rec.invoice_date)[0:10]):
                    raise ValidationError('La fecha de factura no puede ser mayor a la fecha actual.')
                if (str(rec.invoice_date_due)[0:10] < str(rec.invoice_date)[0:10]):
                    raise ValidationError('La fecha de vencimiento no puede ser menor a la fecha de factura.')
                if (len(rec.invoice_line_ids) == 0):
                    raise ValidationError(_('No puede confirmar facturas sin lineas asociadas.'))
                for line in rec.invoice_line_ids:
                    if (line.display_type == 'product' and line.product_id == False):
                        raise ValidationError(_('Las lineas de factura deben presentar un producto asignado.'))
                    if (line.display_type == 'product' and len(line.tax_ids) == 0):
                        raise ValidationError(_('Las lineas de factura deben presentar un impuesto asignado.'))
                    if (line.display_type == 'product' and len(line.tax_ids) > 1):
                        raise ValidationError(_('Las lineas de factura no puede tener mas de un impuesto asignado.'))
                    if (line.display_type == 'product' and line.price_unit == 0):
                        raise ValidationError(_('Las lineas de factura no pueden presentar precio unitario en 0.0.'))
                    if (line.display_type == 'product' and line.price_unit < 0):
                        raise ValidationError(_('Las lineas de factura no pueden presentar precio unitario en negativo.'))
                    if (line.display_type == 'product' and line.quantity == 0):
                        raise ValidationError(_('Las lineas de factura no pueden presentar cantidades en 0.0.'))
                    if (line.display_type == 'product' and line.quantity < 0):
                        raise ValidationError(_('Las lineas de factura no pueden presentar cantidades en negativo.'))
        res = super()._post(soft)
        return res

    def write(self, vals):
        _logger.warning('write-vals: %s', vals)
        if (self.move_type in ['out_invoice', 'in_invoice']):
            invoice_date = datetime.today()
            if ('invoice_date' in vals and str(invoice_date)[0:10] > str(vals['invoice_date'])[0:10]):
                raise ValidationError('La fecha de factura no puede ser inferior a la fecha actual.')
            if ('invoice_date' in vals and str(invoice_date)[0:10] < str(vals['invoice_date'])[0:10]):
                raise ValidationError('La fecha de factura no puede ser mayor a la fecha actual.')
            if ((('invoice_date' in vals and 'invoice_date_due' not in vals) and str(self.invoice_date_due)[0:10] < str(vals['invoice_date'])[0:10]) or (('invoice_date_due' in vals and 'invoice_date' not in vals) and str(vals['invoice_date_due'])[0:10] < str(self.invoice_date)[0:10]) or (('invoice_date_due' in vals and 'invoice_date' in vals) and str(vals['invoice_date_due'])[0:10] < str(vals['invoice_date'])[0:10])):
                raise ValidationError('La fecha de vencimiento no puede ser menor a la fecha de factura.')
        res = super(AccountMove, self).write(vals)
        return res

    def _get_report_base_filename(self):
        for move in self:
            if (move.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']):
                if move.state == 'draft':
                    raise ValidationError(_('No se puede imprimir un documento en estado Borrador.'))
                if move.state == 'cancel':
                    raise ValidationError(_('No se puede imprimir un documento en estado cancelado.'))
                if move.invoice_origin and 'shop' in move.invoice_origin.lower():
                    raise ValidationError(_('Este documento proviene del Punto de Venta y no puede ser impreso desde el módulo de facturación.'))
                if (move.payment_state not in ['not_paid']):
                    #raise ValidationError(_('No se puede imprimir un documento en estado Borrador.'))
                    move.print_count += 1
                #move.print_count += 1
        return super()._get_report_base_filename()