# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2026-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_ve_vat_ledger_import_purchase = fields.Boolean(
        string="Compra de importacion en libro IVA",
        company_dependent=True,
        help=(
            "Si esta activo, las facturas de proveedor de este contacto se "
            "segmentan como compras de importacion en el Libro IVA de compras."
        ),
    )
