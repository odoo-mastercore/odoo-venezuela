###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains('name', 'journal_id', 'state')
    def _check_unique_sequence_number(self):
        payment_group_moves = self.filtered(
            lambda x: x.journal_id.type in ['cash', 'bank'] and x.l10n_latam_document_type_id)
        return super(AccountMove, self - payment_group_moves)._check_unique_sequence_number()
