# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_ve_tax_base_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.l10n_ve_tax_base_account_id',
        readonly=False,
        domain=[('deprecated', '=', False)],
        string="Tax Base Account",
        help="Account that will be set on lines created to represent the tax base amounts.")
