# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################
from odoo import models, fields


class ResCountryStateMunicipalityParish(models.Model):
    _name = 'res.country.state.municipality.parish'
    _description = 'Venezuelan Parish'
    _order = 'name'

    name = fields.Char(
        string='Parroquia',
        size=100,
        required=True,
        help='Nombre de la Parroquia'
    )
    code = fields.Char(
        string='Código',
        size=6,
        required=True,
        help='Código de la Parroquia'
    )
    municipality_id = fields.Many2one(
        'res.country.state.municipality',
        string='Municipio',
        help='Municipio al que pertenece la Parroquia'
    )