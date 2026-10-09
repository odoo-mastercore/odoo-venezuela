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


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ve_vat_ledger_show_import_columns = fields.Boolean(
        string="Segmentar importaciones en Libro IVA de compras",
        default=False,
        help=(
            "Si esta activo, el Libro IVA de compras agrega las columnas de "
            "importacion y segmenta las facturas de los proveedores marcados "
            "como compras de importacion."
        ),
    )
