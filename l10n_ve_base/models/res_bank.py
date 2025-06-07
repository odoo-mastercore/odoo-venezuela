# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import api, models, _
from odoo.exceptions import UserError


class ResBank(models.Model):
    _inherit = 'res.bank'

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ResBank, self).create(vals_list)
        for rec in records:
            if not rec.name:
                raise UserError(
                    _('Debe indicar el Nombre de la Entidad Bancaria.')
                )
        return records

    def write(self, vals):
        res = super(ResBank, self).write(vals)
        if not self.name:
            raise UserError(
                _('Debe indicar el Nombre de la Entidad Bancaria.')
            )
        return res
