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
        reverse_date = self.date if self.date_mode == 'custom' else move.date        
        return {
            'ref': _('Reversal of: %(move_name)s, %(reason)s', move_name=move.name, reason=self.reason)
                   if self.reason
                   else _('Reversal of: %s', move.name),
            'date': reverse_date,
            'invoice_date_due': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id.id,
            'invoice_payment_term_id': None,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': 'at_date' if reverse_date > fields.Date.context_today(self) else 'no',
            'l10n_ve_document_number': ""
        }


    #TODO: ver si esto es necesario.
    # def reverse_moves(self):
    #     """ Forzamos el seteo limpio"""
    #     res = super(AccountMoveReversal, self).reverse_moves()
    #     #Nunca esta pasando por aqui.
    #     for rec in self:
    #         self.move_ids.l10n_ve_document_number = ""
    #     return res
