# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ve_show_vat_ledger_import_fields = fields.Boolean(
        compute="_compute_l10n_ve_show_vat_ledger_import_fields",
    )
    l10n_ve_importation_form_number = fields.Char(
        string="No planilla de importacion",
        copy=False,
    )
    l10n_ve_importation_form_date = fields.Date(
        string="Fecha de planilla de importacion",
        copy=False,
    )
    l10n_ve_importation_file_number = fields.Char(
        string="No de expediente de importacion",
        copy=False,
    )

    @api.depends("partner_id", "company_id", "company_id.l10n_ve_vat_ledger_show_import_columns")
    def _compute_l10n_ve_show_vat_ledger_import_fields(self):
        for move in self:
            if not move.company_id.l10n_ve_vat_ledger_show_import_columns:
                move.l10n_ve_show_vat_ledger_import_fields = False
                continue
            partner = move.partner_id.with_company(move.company_id) if move.partner_id else move.env["res.partner"]
            commercial_partner = partner.commercial_partner_id if partner else move.env["res.partner"]
            move.l10n_ve_show_vat_ledger_import_fields = bool(
                partner
                and (
                    partner.l10n_ve_vat_ledger_import_purchase
                    or commercial_partner.l10n_ve_vat_ledger_import_purchase
                )
            )

    def _get_name_vat_ledger(self):
        return self.name

    def _get_igtf_amount(self):
        return 0

    def _get_igtf_amount_purchase(self):
        return 0

    def _get_reverse_name_vat_ledger(self):
        return self.reversed_entry_id.name

    def _get_debit_name_vat_ledger(self):
        return self.debit_origin_id.name