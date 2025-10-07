# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ve_control_number = fields.Char(
        'Control Number', size=80,
        help="Number used to manage pre-printed invoices, by law you will"
             " need to put here this number to be able to declarate on"
             " Fiscal reports correctly.",store=True)
    l10n_ve_applied_withholding_tax = fields.Boolean(
        'Retencion de IVA aplicada', compute='l10n_ve_compute_applied_withholding',
        store=True, copy=False, default=False)
    l10n_ve_applied_withholding_islr = fields.Boolean(
        'Retencion de ISLR aplicada', compute='l10n_ve_compute_applied_withholding',
        store=True, copy=False, default=False)

    @api.depends('amount_residual', 'amount_residual_signed',)
    def _compute_l10n_ve_applied_withholding(self):
        for move in self:
            l10n_ve_applied_withholding_tax = False
            l10n_ve_applied_withholding_islr = False
            if move.move_type in ['in_invoice'] and move.payment_group_ids:
                if move._get_reconciled_payments().mapped(
                        'payment_group_id').filtered(lambda x: x.iva == True):
                    l10n_ve_applied_withholding_tax = True
                if move._get_reconciled_payments().mapped(
                        'payment_group_id').filtered(lambda x: x.islr == True):
                    l10n_ve_applied_withholding_islr = True
            move.l10n_ve_applied_withholding_tax = l10n_ve_applied_withholding_tax
            move.l10n_ve_applied_withholding_islr = l10n_ve_applied_withholding_islr

    def _post(self, soft=True):
        super(AccountMove, self)._post(soft)
        for move in self:
            if (move.state == 'posted' and move.l10n_ve_control_number == False) or \
                (move.move_type == 'out_refund' and move.l10n_ve_control_number == ''):
                if move.move_type in ['out_invoice', 'out_refund']:
                    if move.journal_id.l10n_ve_sequence_control_id:
                        l10n_ve_control_number = move.env['ir.sequence'].next_by_code(
                            move.journal_id.l10n_ve_sequence_control_id.code)
                        move.write({
                            'l10n_ve_control_number': l10n_ve_control_number
                        })
                    else:
                        raise ValidationError(_(
                            "El diario por el cual está emitiendo la factura no " +
                            "tiene secuencia para número de control"
                        ))