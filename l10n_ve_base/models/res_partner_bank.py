# -*- coding: utf-8 -*-
################################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
################################################################################

from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError

class res_partner_bank(models.Model):
    """inherit for res_partner_bank"""

    _inherit = 'res.partner.bank'
    l10n_ve_acc_type = fields.Selection(
        [
            ('ahorro', 'Cuenta Corriente'),
            ('corriente', 'Cuenta de Ahorro'),
            ('fideicomiso', 'Cuenta Fideicomiso'),

        ],
        string='Tipo de cuenta',
        help=u"Tipo de cuenta."
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

    @api.model
    def create(self, vals):
        if not vals['bank_id']:
            raise exceptions.UserError(
                _(u'Debe Seleccionar la Entidad Bancaria.')
            )
        if not vals['l10n_ve_acc_type']:
            raise exceptions.UserError(
                _(u'Debe seleccionar el tipo de Cuenta.')
            )
        res = super(res_partner_bank, self).create(vals)
        return res

    def write(self, vals):
        if 'bank_id' in vals:
            if not vals.get('bank_id', False):
                raise exceptions.UserError(
                    _(u'Debe Seleccionar la Entidad Bancaria.')
                )
        if 'acc_number' in vals:
            if not vals.get('acc_number', False):
                raise exceptions.UserError(
                    _(u'Debe indicar el numero de cuenta.')
                )
        if 'l10n_ve_acc_type' in vals:
            if not vals.get('l10n_ve_acc_type', False):
                raise exceptions.UserError(
                    _(u'Debe seleccionar el tipo de Cuenta.')
                )
        res = super(res_partner_bank, self).write(vals)
        return res
