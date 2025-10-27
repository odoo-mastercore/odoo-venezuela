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
        'Control Number',
        size=80,
        store=True,
        help="Number used to manage pre-printed invoices, by law you will"
             " need to put here this number to be able to declarate on"
             " Fiscal reports correctly.",
        copy=False
    )
    l10n_ve_withholding_ids = fields.Many2many(
        string='Withholdings',
        comodel_name='l10n_ve.payment.withholding',
        relation='payment_withholding_move_rel',
        column1='withholding_id',
        column2='move_id',
        copy=False,
    )

    def _post(self, soft=True):
        moves_posted = super(AccountMove, self)._post(soft)
        for move in moves_posted:
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
        return moves_posted

    def get_exempt_amount(self):
        self.ensure_one()
        exempt_amount = 0.0
        for line in self.invoice_line_ids:
            if line.tax_ids and line.tax_ids.filtered(lambda r: r.amount == 0):
                exempt_amount += line.price_subtotal
        if self.currency_id != self.company_id.currency_id:
            exempt_amount = exempt_amount * self.inverse_invoice_currency_rate
        return abs(exempt_amount)