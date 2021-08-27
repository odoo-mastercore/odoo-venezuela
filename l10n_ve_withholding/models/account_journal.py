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

    sequence_control_id = fields.Many2one(
        'ir.sequence',
        'Sequence control number',
        copy=False,
        help="Checks numbering sequence.",
    )
    next_control_number = fields.Integer(
        'Next Number Control',
        compute='_compute_next_control_number',
    )
    current_control_number = fields.Integer(
        'Current Number Control',
        compute='_compute_current_control_number',
    )
    @api.depends('sequence_control_id')
    def _compute_next_control_number(self):
        for rec in self:
            if rec.sequence_control_id:
                rec.next_control_number = rec.sequence_control_id.number_next_actual
            else:
                rec.next_control_number = 0

    @api.depends('sequence_control_id')
    def _compute_current_control_number(self):
        for rec in self:
            if rec.sequence_control_id:
                rec.current_control_number = rec.sequence_control_id.\
                    number_next_actual - rec.sequence_control_id.\
                    number_increment
            else:
                rec.current_control_number = 0