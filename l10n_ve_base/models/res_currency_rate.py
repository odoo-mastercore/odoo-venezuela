###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################


from odoo import api, fields, models
from odoo.tools import float_compare
import logging

_logger = logging.getLogger(__name__)


class resCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    rate = fields.Float(
        digits=(16, 16),
        default=1,
        help="The rate of the currency to the currency of rate 1")

class resCurrency(models.Model):
    _inherit = 'res.currency'

    rate = fields.Float(
        compute='_compute_current_rate', 
        string='Current Rate', 
        digits=(16, 16),                
        help='The rate of the currency to the currency of rate 1.')


    def action_get_currency_rate(self):
        currency_id = self.id
        company = self.env['res.company'].search(
            [('country_id', '=', self.env.ref('base.ve').id)],
            limit=1)
        if not company:
            raise UserError(_(
                'No company found using Venezuela localization'))
        return {
            'type': 'ir.actions.act_window',
            'name': ' Currency rate synchronization wizard',
            'res_model': 'currency.rate.wizard',
            'context': {
                'default_currency_id': currency_id,
                'default_company_id': company.id,
            },
            'view_mode': 'form',
            'view_id': self.env.ref(
                'l10n_ve_base.currency_rate_wizard_form').id,
            'target': 'new',
        }
