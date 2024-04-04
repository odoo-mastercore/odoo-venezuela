# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class UniVat(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        recs = super(UniVat, self).create(vals_list)
        self._validate_duplicate_vat(recs)
        return recs

    def write(self, vals):
        res = super(UniVat, self).write(vals)
        if 'vat' in vals:
            self._validate_duplicate_vat(self)
        return res

    def _validate_duplicate_vat(self, partners):
        if not isinstance(partners, models.BaseModel):
            for partner in partners:
                self._validate_single_duplicate_vat(partner)
        else:
            self._validate_single_duplicate_vat(partners)

    def _validate_single_duplicate_vat(self, partner):
        for rec in partner:
            if rec.vat:
                same_vats = self.env['res.partner'].search([
                    ('vat', '=', rec.vat),
                    ('parent_id','=',False),
                    ('l10n_latam_identification_type_id', '=', rec.l10n_latam_identification_type_id.id),
                ])
                if len(same_vats)>1:
                    raise ValidationError(
                                _('Ya se encuentra registrado el Número de Identificación %s para el Contacto (%s)') % (rec.vat, same_vats[0].name))

    
    @api.constrains('vat')
    def _constrains_validate_vat(self):
        for rec in self:
            validate = True
            if rec.vat:
                validate = rec.vat.isdigit()
            else:
                raise UserError(_('El Número de Identificación es requerido'))
            if not validate:
                raise UserError(_('El Número de Identificación %s sólo debe contener números') % (rec.vat))