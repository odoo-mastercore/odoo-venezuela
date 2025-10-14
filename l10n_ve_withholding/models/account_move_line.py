# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_ve_withholding_line_id = fields.Many2one(
        "l10n_ve.payment.withholding",
        string="Withholding line"
    )

