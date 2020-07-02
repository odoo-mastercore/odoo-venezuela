###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def open_payments_action(self, payment_type, mode='tree'):
        if payment_type == 'transfer':
            ctx = self._context.copy()
            ctx.update({
                'default_payment_type': payment_type,
                'default_journal_id': self.id
            })
            ctx.pop('group_by', None)
            action_rec = self.env['ir.model.data'].xmlid_to_object(
                'l10n_ve_account_payment.action_account_payments_transfer')
            action = action_rec.read([])[0]
            action['context'] = ctx
            action['domain'] = [('journal_id', '=', self.id),
                                ('payment_type', '=', payment_type)]
            return action
        return super(AccountJournal, self).open_payments_action(payment_type, mode=mode)
