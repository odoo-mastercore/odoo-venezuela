# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_ve_sequence_control_id = fields.Many2one(
        'ir.sequence',
        'Sequence control number',
        copy=False,
        help="Checks numbering sequence.",
    )
    l10n_ve_next_control_number = fields.Integer(
        'Next Number Control',
        compute='_compute_l10n_ve_next_control_number',
    )
    l10n_ve_current_control_number = fields.Integer(
        'Current Number Control',
        compute='_compute_l10n_ve_current_control_number',
    )
    l10n_ve_apply_iva = fields.Boolean('¿Utilizar diario para Aplicar Retención IVA?')
    l10n_ve_apply_islr = fields.Boolean('¿Utilizar diario para Aplicar Retención ISLR?')

    @api.depends('l10n_ve_sequence_control_id')
    def _compute_l10n_ve_next_control_number(self):
        for journal in self:
            next_control_number = 0
            if journal.l10n_ve_sequence_control_id:
                next_control_number = journal.l10n_ve_sequence_control_id.number_next_actual
            journal.l10n_ve_next_control_number = next_control_number

    @api.depends('l10n_ve_sequence_control_id')
    def _compute_l10n_ve_current_control_number(self):
        for journal in self:
            control_number = 0
            if journal.l10n_ve_sequence_control_id:
                control_number = journal.l10n_ve_sequence_control_id.number_next_actual - journal.l10n_ve_sequence_control_id.number_increment
            journal.l10n_ve_current_control_number = control_number