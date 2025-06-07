# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################
from odoo import models, fields


class resCountryStateMunicipality(models.Model):
    _name = 'res.country.state.municipality'
    _description = 'Municipality'
    _order = 'name'

    name = fields.Char(
        string='Municipio',
        size=100,
        required=True,
        help='Nombre del Municipio'
    )
    code = fields.Char(
        string='Código',
        size=5,
        required=True,
        help='Código de Municipio'
    )
    state_id = fields.Many2one(
        'res.country.state',
        string='Estado',
        help='Estado al que pertenece el Municipio'
    )
    parish_ids = fields.One2many(
        string="Parroquias",
        comodel_name="res.country.state.municipality.parish",
        inverse_name="municipality_id",
        help="Parroquias del Municipio",
    )