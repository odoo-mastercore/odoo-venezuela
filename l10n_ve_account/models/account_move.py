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
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)


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
                rec.l10n_ve_invoice_date = fields.Datetime.now()

    def _get_l10n_ve_invoice_date(self, split=False):
        date, time = False, False
        if self.l10n_ve_invoice_date:
            date_tz = fields.Datetime.context_timestamp(self, self.l10n_ve_invoice_date)
            date = date_tz.strftime("%d-%m-%Y")
            time = date_tz.strftime("%H:%M:%S")
        if split:
            return (date, time)
        return f"{date} {time}" if date else False