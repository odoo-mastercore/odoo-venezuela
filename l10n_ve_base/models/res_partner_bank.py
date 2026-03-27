###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2025-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    l10n_ve_acc_type = fields.Selection(
        [
            ('ahorro', 'Cuenta Corriente'),
            ('corriente', 'Cuenta de Ahorro'),
            ('fideicomiso', 'Cuenta Fideicomiso'),
        ],
        string='Tipo de cuenta',
        help="Tipo de cuenta."
    )

    @api.onchange('bank_id')
    def _onchange_bank_id(self):
        if self.bank_id:
            number = self.bank_id.bic
            return {
                'value': {'acc_number': number}
            }
        else:
            return {
                'value': {'acc_number': ''},
            }

    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super(ResPartnerBank, self).create(vals_list)
    #     for rec in records:
    #         if not rec.bank_id:
    #             raise UserError(_('Debe Seleccionar la Entidad Bancaria.'))
    #     return records

    # def write(self, vals):
    #     rec = super(ResPartnerBank, self).write(vals)
    #     if not self.bank_id:
    #         raise UserError(_('Debe Seleccionar la Entidad Bancaria.'))
    #     if not self.acc_number:
    #         raise UserError(_('Debe indicar el numero de cuenta.'))
    #     return rec