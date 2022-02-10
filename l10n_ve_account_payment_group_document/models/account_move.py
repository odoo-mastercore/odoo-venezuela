# © 2020 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains('name', 'journal_id', 'state')
    def _check_unique_sequence_number(self):
        payment_group_moves = self.filtered(
            lambda x: x.journal_id.type in ['cash', 'bank'] and x.payment_id.payment_group_id)
        return super(AccountMove, self - payment_group_moves)._check_unique_sequence_number()
