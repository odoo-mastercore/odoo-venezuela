# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2024-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################

from odoo import models, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('l10n_latam_identification_type_id','company_type')
    def _constrains_validate_document_type(self):
        document_type_person =['V', 'P', 'E']
        document_type_company =['J', 'G', 'C']
        for record in self:
            if record.company_type == 'person' and len(record.parent_id)==0:
                if record.l10n_latam_identification_type_id.l10n_ve_code not in document_type_person:
                    raise ValidationError('El tipo de identificación no corresponde con la compañía tipo persona')
            elif record.company_type == 'company':
                if record.l10n_latam_identification_type_id.l10n_ve_code not in document_type_company:
                    raise ValidationError('El tipo de identificación no corresponde con la compañía tipo compañía')
