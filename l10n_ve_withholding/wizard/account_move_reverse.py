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
        return {
            'ref': _('Reversal of: %s, %s') % (move.name, self.reason) if self.reason else _('Reversal of: %s') % (move.name),
            'date': self.date or move.date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
            'invoice_payment_term_id': None,
            'auto_post': True if self.date > fields.Date.context_today(self) else False,
            'invoice_user_id': move.invoice_user_id.id,
            'l10n_ve_document_number': ""
        }


    # def reverse_moves(self):
    #     """ Forzamos fecha de la factura original para que el amount total de la linea se calcule bien"""
    #     res = super(AccountMoveReversal, self).reverse_moves()
    #     for rec in self:
    #         self.move_ids.l10n_ve_document_number = ""
    #     return res
