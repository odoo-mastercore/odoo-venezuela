# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ve_tax_base_account_id = fields.Many2one(
        comodel_name='account.account',
        domain=[('deprecated', '=', False)],
        string="Tax Base Account",
        help="Account that will be set on lines created to represent the tax base amounts."
    )
    l10n_ve_withholding_signature = fields.Image(
        string='Withholding Signature',
        max_width=200,
        max_height=200
    )

    def _localization_use_withholdings(self):
        """ This method is to be inherited by localizations and return True
            if localization use documents """
        self.ensure_one()
        if self.country_id == self.env.ref('base.ve'):
            return True
        else:
            return False
