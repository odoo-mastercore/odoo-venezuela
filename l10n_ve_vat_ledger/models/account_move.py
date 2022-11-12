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