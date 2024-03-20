# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2024-Present.
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
        rec = super(UniVat, self).create(vals_list)
        for val in vals_list:
            if val.get('l10n_latam_identification_type_id'):
                company_type = val.get('company_type')
                identification_type_id = self.env['l10n_latam.identification.type']\
                    .browse(int(val.get('l10n_latam_identification_type_id')))
                if identification_type_id.l10n_ve_code in ['J','G','C'] and company_type == 'person':
                    raise ValidationError('El tipo de identificación no corresponde con el tipo de compañia')
                
                if identification_type_id.l10n_ve_code in ['V','P','E'] and company_type == 'company':
                    raise ValidationError('El tipo de identificación no corresponde con el tipo de compañia')
                    
        return rec

    def write(self, vals):
        res = super(UniVat, self).write(vals)
        if 'l10n_latam_identification_type_id' in vals:
            identification_type_id = self.env['l10n_latam.identification.type']\
                    .browse(int(vals.get('l10n_latam_identification_type_id')))
            if identification_type_id.l10n_ve_code in ['J','G','C'] and self.company_type == 'person':
                    raise ValidationError('El tipo de identificación no corresponde con el tipo de compañia')
                
            if identification_type_id.l10n_ve_code in ['V','P','E'] and self.company_type == 'company':
                raise ValidationError('El tipo de identificación no corresponde con el tipo de compañia')
            
        elif 'company_type' in vals:
            if self.l10n_latam_identification_type_id.l10n_ve_code in ['J','G','C'] and vals.get('company_type') == 'person':
                    raise ValidationError('El tipo de identificación no corresponde con el tipo de compañia')
                
            if self.l10n_latam_identification_type_id.l10n_ve_code in ['V','P','E'] and vals.get('company_type') == 'company':
                raise ValidationError('El tipo de identificación no corresponde con el tipo de compañia')
            
        elif 'l10n_latam_identification_type_id' in vals and 'company_type' in vals:
            identification_type_id = self.env['l10n_latam.identification.type']\
                    .browse(int(vals.get('l10n_latam_identification_type_id')))
            if identification_type_id.l10n_ve_code in ['J','G','C'] and vals.get('company_type') == 'person':
                    raise ValidationError('El tipo de identificación no corresponde con el tipo de compañia')
                
            if identification_type_id.l10n_ve_code in ['V','P','E'] and vals.get('company_type') == 'company':
                raise ValidationError('El tipo de identificación no corresponde con el tipo de compañia')

        return res