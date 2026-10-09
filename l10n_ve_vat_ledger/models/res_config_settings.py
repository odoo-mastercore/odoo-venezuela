# -*- coding: utf-8 -*-
##############################################################################
# Author: Mastercore Sinapsys Global®
# Copyright: 2019-Present.
# License OPL-1 (Odoo Proprietary License v1.0)
# See https://www.odoo.com/documentation/master/legal/licenses.html
#
#
##############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ve_vat_ledger_show_import_columns = fields.Boolean(
        related="company_id.l10n_ve_vat_ledger_show_import_columns",
        readonly=False,
        string="Segmentar importaciones en Libro IVA de compras",
    )
