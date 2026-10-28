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
