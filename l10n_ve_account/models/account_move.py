# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ve_invoice_date = fields.Datetime(
        string='Fecha y hora de la factura',
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

    def _check_lines_price(self):
        FORBIDDEN_PATTER = r'\b(descuento|desc|des|discount)\b'
        """
          Para descuentos en líneas de factura, se permite el precio cero o negativo,
          dejamos el comodin de 'skip_check_price' para que no se valide el precio
          en caso de que se necesite validar el precio en otro momento.
        """
        if 'skip_check_price' in self._context:
            return True
        for line in self.invoice_line_ids:
            if line.price_unit <= 0 and\
                self.move_type in ['out_invoice'] and not\
                re.search(FORBIDDEN_PATTER, line.product_id.name or '', re.IGNORECASE):
                raise ValidationError(
                    _("No se permiten precios cero o negativos en las líneas de factura. Línea con producto: %s")
                    % line.product_id.display_name
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AccountMove, self).create(vals_list)
        for rec in records:
            rec._check_lines_price()
        return records

    def write(self, vals):
        rec = super(AccountMove, self).write(vals)
        if any(field in vals for field in ('line_ids', 'invoice_line_ids')):
            self._check_lines_price()
        return rec
