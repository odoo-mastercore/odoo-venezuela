# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2026-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ve_vat_ledger_show_import_columns = fields.Boolean(
        related="company_id.l10n_ve_vat_ledger_show_import_columns",
        readonly=False,
        string="Segmentar importaciones en Libro IVA de compras",
    )
