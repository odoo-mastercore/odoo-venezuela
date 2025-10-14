# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models


class AccountDebitNoteInherit(models.TransientModel):
    _inherit = 'account.debit.note'

    def _prepare_default_values(self, move):
        values = super(AccountDebitNoteInherit,self)._prepare_default_values(move)
        values.update({'l10n_ve_control_number': False})
        return values