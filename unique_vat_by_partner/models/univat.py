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

        for rec in recs:
            if rec.vat:
                same_vat = self.env['res.partner'].search([
                    ('vat', '=', rec.vat),
                    ('id', '!=', rec.id),
                    ('l10n_latam_identification_type_id', '=',
                        rec.l10n_latam_identification_type_id.id),
                ])

                if same_vat:
                    child = []
                    if rec.child_ids:
                        child = [p.id for p in rec.child_ids]
                    if rec.parent_id:
                        child.append(rec.parent_id.id)
                    if same_vat.id not in child:
                        raise ValidationError(
                            _('Ya se encuentra registrado el Número de Identificación %s para el Contacto (%s)') % (rec.vat, same_vat.name))

        return recs