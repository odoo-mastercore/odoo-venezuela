###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import logging

_logger = logging.getLogger(__name__)


class CurrencyRateWizard(models.TransientModel):
    _name = 'currency.rate.wizard'
    _description = 'Currency Rate Wizard'

    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
    )
    number = fields.Float(
        string='Tasa en Bs',
        required=True,
        digits=(16, 2),
    )

    def confirm(self):
        self.ensure_one()
        rate = format(1 / self.number, '.16f')
        values = {
            'rate': rate,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
        }
        rec = self.env['res.currency.rate'].search([
            ('currency_id', '=', self.currency_id.id),
            ('name', '=', datetime.date.today())
        ])

        if rec:
            rec.write(values)
        else:
            record = self.env['res.currency.rate'].create(values)

        return {
            'type': 'ir.actions.act_window',
            'name': ' Done!',
            'res_model': 'currency.rate.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref(
                    'l10n_ve_base.consult_currency_wizard_confirm').id,
            'target': 'new',
        }
