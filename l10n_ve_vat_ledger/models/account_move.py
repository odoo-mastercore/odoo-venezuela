from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
from ast import literal_eval
import logging
import io
from io import BytesIO
import xlsxwriter
import shutil
import base64
import csv
import xlwt
import json
from dateutil.relativedelta import relativedelta, MO
from json import JSONDecodeError
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('reversed_entry_id')
    def _compute_reversed_entry_code(self):
        for rec in self:
            rec.reversed_entry_code = str(rec.reversed_entry_id.sequence_number).rjust(5, '0')


    reversed_entry_code = fields.Char(compute='_compute_reversed_entry_code')

    def invoice_rate(self, currency_id, invoice_date):
        for rec in self:
            last_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', currency_id),
                ('name', '<=', invoice_date)
            ], limit=1).rate
            if not last_rate:
                last_rate = 1
            return last_rate

    def amount_str_in_company_currency(self, amount, currency_id, date):
        for rec in self:
            result = 0.00
            if currency_id and date:
                rate = rec.invoice_rate(currency_id, date)
                if amount.split('$'):
                    amount_float = round(float(amount.replace(
                        '.', '').replace(',', '.').split('$')[1]), 4)
                result = round(amount_float * (1/rate), 4)
            return result
