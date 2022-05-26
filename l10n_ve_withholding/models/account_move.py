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
    _inherit = "account.move"

    l10n_ve_document_number = fields.Char(
        'Control Number', size=80,
        help="Number used to manage pre-printed invoices, by law you will"
             " need to put here this number to be able to declarate on"
             " Fiscal reports correctly.",store=True)

    def get_taxes_values(self):
        """
        Hacemos esto para disponer de fecha de factura y cia para calcular
        impuesto con código python.
        Aparentemente no se puede cambiar el contexto a cosas que se llaman
        desde un onchange (ver https://github.com/odoo/odoo/issues/7472)
        entonces usamos este artilugio
        """
        invoice_date = self.invoice_date or fields.Date.context_today(self)
        # hacemos try porque al llamarse desde acciones de servidor da error
        try:
            self.env.context.invoice_date = invoice_date
            self.env.context.invoice_company = self.company_id
        except Exception:
            pass
        return super().get_taxes_values()

    def _post(self, soft):
        super(AccountMove, self)._post(soft)
        for rec in self:
            if (rec.state == 'posted' and rec.\
                l10n_ve_document_number == False) or rec.\
                    move_type == 'out_refund' and rec.l10n_ve_document_number == '':
                if rec.move_type in ['out_invoice', 'out_refund']:
                    if rec.journal_id.sequence_control_id:        
                        l10n_ve_document_number = rec.env[
                            'ir.sequence'].next_by_code(rec.journal_id.\
                                sequence_control_id.code)
                        rec.write({
                            'l10n_ve_document_number': l10n_ve_document_number})
                    else:
                        raise ValidationError(
                    _("El diario por el cual está emitiendo la factura no"+
                        " tiene secuencia para número de control"))

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_price(self):
        # ver nota en get_taxes_values
        invoice = self.move_id
        invoice_date = invoice.invoice_date or fields.Date.context_today(self)
        # hacemos try porque al llamarse desde acciones de servidor da error
        try:
            self.env.context.invoice_date = invoice_date
            self.env.context.invoice_company = self.company_id
        except Exception:
            pass
        return super()._compute_price()
