# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ve_invoice_date = fields.Datetime(
        string='Invoice Date and Time',
        readonly=True
    )

    def _post(self, soft=True):
        super()._post(soft=soft)
        for rec in self:
            if rec.state == 'posted':
                rec.l10n_ve_invoice_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.now())