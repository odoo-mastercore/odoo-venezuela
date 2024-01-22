# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountDebitNoteInherit(models.TransientModel):

    _inherit = 'account.debit.note'

    def _prepare_default_values(self, move):
        res = super(AccountDebitNoteInherit,self)._prepare_default_values(move)
        
        res.update({
            'l10n_ve_document_number': False
        })
        return res