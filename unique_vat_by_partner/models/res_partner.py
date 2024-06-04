# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################

from odoo import api, models, _
from odoo.exceptions import ValidationError, UserError

class UniVat(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat','l10n_latam_identification_type_id','company_type')
    def _validate_single_duplicate_vat(self):
        for rec in self:
            #Validación
            if rec.vat and rec.country_id.code == 'VE':
                same_vats = self.env['res.partner'].search([
                    ('vat', '=', rec.vat),
                    ('parent_id','=',False),
                    ('active','=',True),
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