# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    country_id = fields.Many2one(
        'res.country',
        string='País',
        ondelete='restrict',
        help="País",
        default=lambda self: self.env['res.country'].search(
            [('name', '=', 'Venezuela')]
        )[0].id
    )
    state_id = fields.Many2one(
        "res.country.state",
        string='Estado',
        ondelete='restrict',
        help="Estado"
    )
    municipality_id = fields.Many2one(
        "res.country.state.municipality",
        string="Municipio",
        domain="[('state_id', '=', state_id)]",
        ondelete='restrict',
        help="Municipio"
    )
    parish_id = fields.Many2one(
        "res.country.state.municipality.parish",
        string="Parroquia",
        ondelete='restrict',
        domain="[('municipality_id', '=', municipality_id)]",
        help="Parroquia"
    )
    l10n_latam_identification_type_id = fields.Many2one(
        'l10n_latam.identification.type', string="Identification Type",
        index=True, auto_join=True,
        default=lambda self: self.env.ref('l10n_ve_base.it_civ') or False,
        help="The type of identification")
    l10n_ve_responsibility_type_id = fields.Many2one(
        'l10n_ve.responsibility.type', string='SENIAT Responsibility Type',
        index=True, help='Defined by SENIAT to identify the type of '
        'responsibilities that a person or a legal entity could have and that '
        'impacts in the type of operations and requirements they need.')

    @api.constrains('vat', 'l10n_latam_identification_type_id')
    def check_vat(self):
        """ Since we validate more documents than the vat for Venezuelan partners (RIF, CI) we
        extend this method in order to process it. """
        l10n_ve_partners = self.filtered(lambda x: x.l10n_latam_identification_type_id)
        return super(ResPartner, self - l10n_ve_partners).check_vat()

    def _check_unique_vat(self):
        if self.vat:
            same_vat = self.env['res.partner'].search([
                ('vat', '=', self.vat),
                ('id', '!=', self.id),
                ('l10n_latam_identification_type_id', '=',
                    self.l10n_latam_identification_type_id.id),
            ])
            if same_vat:
                child = []
                if self.child_ids:
                    child = [p.id for p in self.child_ids]
                if self.parent_id:
                    child.append(self.parent_id.id)
                if same_vat[0].id not in child:
                    raise ValidationError(_(
                        'Ya se encuentra registrado el Número de Identificación %s para el Contacto (%s)'
                    ) % (self.vat, same_vat[0].name))

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ResPartner, self).create(vals_list)
        for record in records:
            record._check_unique_vat()
        return records

    def write(self, vals):
        rec = super(ResPartner, self).write(vals)
        if 'vat' in vals:
            self._check_unique_vat()
        return rec