# -*- coding: utf-8 -*-
###############################################################################
# Author      : SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyright(c): 2021-Present.
# License URL : AGPL-3
###############################################################################
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):

    _inherit = 'account.move'

    def invoice_rate(self, currency_id, invoice_date):
        for rec in self:
            last_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', currency_id),
                ('name', '=', invoice_date)
            ],limit=1).rate
            if not last_rate:
                last_rate = 1
            return last_rate

    def amount_str_in_company_currency(self, amount, currency_id, date):
        for rec in self:
            result = 0.00
            if currency_id and date:
                rate = rec.invoice_rate(currency_id,date)
                if amount.split('$ '):
                    amount_float = round(float(
                        amount.replace(',', '.').split('$ ')[1]), 2)
                result = amount_float * (1/rate)
            return result
