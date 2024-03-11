# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

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
        if partner.vat:
            same_vats = self.env['res.partner'].search([
                ('vat', '=', partner.vat),
                ('id', '!=', partner.id),
                ('l10n_latam_identification_type_id', '=', partner.l10n_latam_identification_type_id.id),
            ])

            for same_vat in same_vats:
                child = []
                if partner.child_ids:
                    child = [p.id for p in partner.child_ids]
                if partner.parent_id:
                    child.append(partner.parent_id.id)
                if same_vat.id not in child:
                    raise ValidationError(
                        _('Ya se encuentra registrado el Número de Identificación %s para el Contacto (%s)') % (partner.vat, same_vat.name))