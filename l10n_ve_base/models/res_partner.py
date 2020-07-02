# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    country_id = fields.Many2one(
        'res.country',
        string=u'País',
        ondelete='restrict',
        help=u"País",
        default=lambda self: self.env['res.country'].search(
            [('name', '=', 'Venezuela')]
        )[0].id
    )
    state_id = fields.Many2one(
        "res.country.state",
        string='Estado',
        ondelete='restrict',
        help=u"Estado"
    )
    municipality_id = fields.Many2one(
        "res.country.state.municipality",
        string="Municipio",
        domain="[('state_id', '=', state_id)]",
        ondelete='restrict',
        help=u"Municipio"
    )
    parish_id = fields.Many2one(
        "res.country.state.municipality.parish",
        string="Parroquia",
        ondelete='restrict',
        domain="[('municipality_id', '=', municipality_id)]",
        help=u"Parroquia"
    )
    l10n_latam_identification_type_id = fields.Many2one(
        'l10n_latam.identification.type', string="Identification Type",
        index=True, auto_join=True,
        # default=lambda self: self.env.ref('l10n_ve_base.it_civ'),
        help="The type of identification")
    l10n_ve_responsibility_type_id = fields.Many2one(
        'l10n_ve.responsibility.type', string='SENIAT Responsibility Type', 
        index=True, help='Defined by SENIAT to identify the type of '
        'responsibilities that a person or a legal entity could have and that '
        'impacts in the type of operations and requirements they need.')

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            return {
                'value': {
                    'municipality_id': '',
                    'parish_id': ''
                },
                'domain': {
                    'municipality_id': [
                        ('state_id', '=', self.state_id.id)
                    ]
                },
            }
        else:
            return {'domain': {'state_id': []}}

    @api.onchange('municipality_id')
    def _onchange_municipality_id(self):
        if self.municipality_id:
            return {'value': {'parish_id': ''}}

    @api.onchange('country_id')
    def _onchange_country(self):
        return {
            'value': {
                'l10n_ve_responsibility_type_id': ''
            },
        }
