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

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (len(vals['order_line']) == 0):
                raise ValidationError(_('No puede guardar pedidos de venta sin lineas asociadas.'))
            date_order = datetime.today()
            if (str(date_order)[0:10] > str(vals['date_order'])[0:10]):
                raise ValidationError('La fecha de cotización no puede ser inferior a la fecha actual.')
            if (str(date_order)[0:10] < str(vals['date_order'])[0:10]):
                raise ValidationError('La fecha de cotización no puede ser mayor a la fecha actual.')
            if (str(vals['validity_date'])[0:10] < str(vals['date_order'])[0:10]):
                raise ValidationError('La fecha de vencimiento no puede ser menor a la fecha de cotización.')
            for line in vals['order_line']:
                if (line[2]['product_template_id'] != False and len(line[2]['tax_id']) == 0):
                    raise ValidationError(_('Las lineas de pedidos deben presentar un impuesto asignado.'))
                if (line[2]['product_template_id'] != False and len(line[2]['tax_id']) > 1):
                    raise ValidationError(_('Las lineas de pedidos no puede tener mas de un impuesto asignado.'))
                if (line[2]['product_template_id'] != False and line[2]['price_unit'] == 0):
                    raise ValidationError(_('Las lineas de pedidos no pueden presentar precio unitario en 0.0.'))
                if (line[2]['product_template_id'] != False and line[2]['price_unit'] < 0):
                    raise ValidationError(_('Las lineas de pedidos no pueden presentar precio unitario en negativo.'))
                if (line[2]['product_template_id'] != False and line[2]['product_uom_qty'] == 0):
                    raise ValidationError(_('Las lineas de pedidos no pueden presentar cantidades en 0.0.'))
                if (line[2]['product_template_id'] != False and line[2]['product_uom_qty'] < 0):
                    raise ValidationError(_('Las lineas de pedidos no pueden presentar cantidades en negativo.'))
        res = super().create(vals_list)
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if (len(self.order_line) == 0):
            raise ValidationError(_('No puede guardar pedidos de venta sin lineas asociadas.'))
        date_order = datetime.today()
        if (str(date_order)[0:10] > str(self.date_order)[0:10]):
            raise ValidationError('La fecha de cotización no puede ser inferior a la fecha actual.')
        if (str(date_order)[0:10] < str(self.date_order)[0:10]):
            raise ValidationError('La fecha de cotización no puede ser mayor a la fecha actual.')
        if (str(self.validity_date)[0:10] < str(self.date_order)[0:10]):
            raise ValidationError('La fecha de vencimiento no puede ser menor a la fecha de cotización.')
        for line in self.order_line:
            if (line.product_template_id != False and len(line.tax_id) == 0):
                raise ValidationError(_('Las lineas de pedidos deben presentar un impuesto asignado.'))
            if (line.product_template_id != False and len(line.tax_id) > 1):
                raise ValidationError(_('Las lineas de pedidos no puede tener mas de un impuesto asignado.'))
            if (line.product_template_id != False and line.price_unit == 0):
                raise ValidationError(_('Las lineas de pedidos no pueden presentar precio unitario en 0.0.'))
            if (line.product_template_id != False and line.price_unit < 0):
                raise ValidationError(_('Las lineas de pedidos no pueden presentar precio unitario en negativo.'))
            if (line.product_template_id != False and line.product_uom_qty == 0):
                raise ValidationError(_('Las lineas de pedidos no pueden presentar cantidades en 0.0.'))
            if (line.product_template_id != False and line.product_uom_qty < 0):
                raise ValidationError(_('Las lineas de pedidos no pueden presentar cantidades en negativo.'))
        return res

    '''def _get_order_lines_to_report(self):
        if (self.state != 'sale'):
            raise ValidationError(_('2No se pueden imprimir pedidos que no se encuentren confirmados.'))
        return super()._get_order_lines_to_report()'''