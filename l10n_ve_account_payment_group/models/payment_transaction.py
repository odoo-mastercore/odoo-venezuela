##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class PaymentTransaction(models.Model):

    _inherit = 'payment.transaction'

    def _reconcile_after_transaction_done(self):
        # Validate invoices automatically upon the transaction is posted.
        invoices = self.mapped('invoice_ids').filtered(lambda inv: inv.state == 'draft')
        invoices.action_post()

        # Create & Post the payments.
        for trans in self:
            if trans.payment_id:
                continue

            trans._create_payment()