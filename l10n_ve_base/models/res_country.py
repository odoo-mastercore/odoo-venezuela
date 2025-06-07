# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################
from odoo import models, fields


class ResCountry(models.Model):
    _inherit = 'res.country'

    nationality = fields.Char(
        string='Nacionalidad',
        required=False,
        help='Nacionalidad'
    )