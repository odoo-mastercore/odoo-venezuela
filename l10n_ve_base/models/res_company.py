# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################
from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

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
        default=lambda self: self.env.ref('l10n_ve_base.it_rifj', raise_if_not_found=False),
        help="The type of identification")
    l10n_ve_responsibility_type_id = fields.Many2one(
        'l10n_ve.responsibility.type', string='SENIAT Responsibility Type',
        index=True, help='Defined by SENIAT to identify the type of '
        'responsibilities that a person or a legal entity could have and that '
        'impacts in the type of operations and requirements they need.')