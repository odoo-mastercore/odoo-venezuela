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


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (len(vals['taxes_id']) == 0):
                raise ValidationError(_('El producto requiere un impuesto asignado.'))
            if (len(vals['taxes_id']) > 1):
                raise ValidationError(_('El producto no puede tener mas de un impuesto asignado.'))
            if (vals['list_price'] == 0):
                raise ValidationError(_('El precio del producto no puede ser 0.0.'))
            if (vals['list_price'] < 0):
                raise ValidationError(_('El precio del producto no puede ser negativo.'))
        res = super().create(vals_list)
        return res

    def write(self, vals):
        if ('list_price' in vals and vals['list_price'] == 0):
            raise ValidationError(_('El precio del producto no puede ser 0.0.'))
        if ('list_price' in vals and vals['list_price'] < 0):
            raise ValidationError(_('El precio del producto no puede ser negativo.'))
        res = super(ProductTemplate, self).write(vals)
        if (len(self.taxes_id) == 0):
            raise ValidationError(_('El producto requiere un impuesto asignado.'))
        if (len(self.taxes_id) > 1):
            raise ValidationError(_('El producto no puede tener mas de un impuesto asignado.'))
        return res