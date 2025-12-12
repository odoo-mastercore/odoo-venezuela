# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'


    def _prepare_default_reversal(self, move):
        reverse_vals = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        reverse_vals.update({
            'l10n_ve_document_number': "",
            'invoice_origin': move.ref,
        })
        return reverse_vals


    #TODO: ver si esto es necesario.
    # def reverse_moves(self):
    #     """ Forzamos el seteo limpio"""
    #     res = super(AccountMoveReversal, self).reverse_moves()
    #     #Nunca esta pasando por aqui.
    #     for rec in self:
    #         self.move_ids.l10n_ve_document_number = ""
    #     return res
