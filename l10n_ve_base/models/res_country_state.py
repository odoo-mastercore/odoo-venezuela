# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################
from odoo import models, fields


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    municipality_ids = fields.One2many(
        string="Municipios",
        comodel_name="res.country.state.municipality",
        inverse_name="state_id",
        help="Municipios del Estado",
    )
