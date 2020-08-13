# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################
from odoo import models, fields


class Parish(models.Model):
    """Modelo Parish."""

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


class Municipality(models.Model):
    """Modelo Municipality."""

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
        string=u'Código',
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


class State(models.Model):
    """Modelo extendido res.country.state."""

    _inherit = 'res.country.state'
    municipality_ids = fields.One2many(
        string="Municipios",
        comodel_name="res.country.state.municipality",
        inverse_name="state_id",
        help="Municipios del Estado",
    )


class Country(models.Model):
    """Modelo extendido res.country."""

    _inherit = 'res.country'
    nationality = fields.Char(
        string='Nacionalidad',
        required=False,
        help='Nacionalidad'
    )
