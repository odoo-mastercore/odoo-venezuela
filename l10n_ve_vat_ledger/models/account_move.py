# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_name_vat_ledger(self):
        return self.name

    def _get_igtf_amount(self):
        return 0

    def _get_igtf_amount_purchase(self):
        return 0

    def _get_reverse_name_vat_ledger(self):
        return self.reversed_entry_id.name

    def _get_debit_name_vat_ledger(self):
        return self.debit_origin_id.name