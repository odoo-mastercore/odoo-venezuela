# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)



class AccountVatLedger(models.Model):

    _name = "account.vat.ledger"
    _description = "Account VAT Ledger"
    _inherit = ['mail.thread']
    _order = 'date_from desc'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env[
            'res.company']._company_default_get('account.vat.ledger')
    )
    type = fields.Selection(
        [('sale', 'Sale'), ('purchase', 'Purchase')],
        "Type",
        required=True
    )
    date_from = fields.Date(
        string='Start Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    journal_ids = fields.Many2many(
        'account.journal', 'account_vat_ledger_journal_rel',
        'vat_ledger_id', 'journal_id',
        string='Journals',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('presented', 'Presented'), ('cancel', 'Cancel')],
        'State',
        required=True,
        default='draft'
    )
    note = fields.Html(
        "Notes"
    )
    
    # Computed fields
    name = fields.Char(
        'Title',
        compute='_compute_name'
    )
    reference = fields.Char(
        'Reference',
    )
    invoice_ids = fields.Many2many(
        'account.move',
        string="Invoices",
        compute="_compute_invoices",
        store=True
    )

    @api.depends('journal_ids', 'date_from', 'date_to')
    def _compute_invoices(self):
        for rec in self:
            invoices_domain = []

            invoices_domain += [
                ('state', '!=', 'draft'),
                # ('l10n_ve_document_number', '!=', False),
                ('journal_id', 'in', rec.journal_ids.ids),
                ('company_id', '=', rec.company_id.id),
            ]
            if rec.type == 'sale':
                invoices_domain += [
                    ('move_type', 'in',['out_invoice', 'out_refund']),
                    ('invoice_date', '>=', rec.date_from),
                    ('invoice_date', '<=', rec.date_to),]
            elif rec.type == 'purchase':
                invoices_domain += [
                    ('move_type', 'in',['in_invoice', 'in_refund']),
                    ('date', '>=', rec.date_from),
                    ('date', '<=', rec.date_to),]
            rec.invoice_ids = rec.env['account.move'].search(invoices_domain,
                order='invoice_date desc, l10n_ve_document_number desc')
    
    @api.depends('type', 'reference',)
    def _compute_name(self):
        date_format = self.env['res.lang']._lang_get(
            self._context.get('lang', 'en_US')).date_format
        for rec in self:
            if rec.type == 'sale':
                ledger_type = _('Sales')
            elif rec.type == 'purchase':
                ledger_type = _('Purchases')
            if rec.date_from and rec.date_to:
                name = _("Libro IVA ({0})  {1} - {2}").format(
                    ledger_type,
                    rec.date_from and fields.Date.from_string(
                        rec.date_from).strftime(date_format) or '',
                    rec.date_to and fields.Date.from_string(
                        rec.date_to).strftime(date_format) or ''
                )
            else:
                name = _("Libro IVA (%s)") % (
                    ledger_type,
                )
            if rec.reference:
                name = "%s - %s" % (name, rec.reference)
            rec.name = name

 

    @api.onchange('company_id')
    def change_company(self):
        if self.type == 'sale':
            domain = [('type', '=', 'sale')]
        elif self.type == 'purchase':
            domain = [('type', '=', 'purchase')]
        domain += [('company_id', '=', self.company_id.id),]
        journals = self.env['account.journal'].search(domain)
        self.journal_ids = journals

    def action_present(self):
        self.state = 'presented'

    def action_cancel(self):
        self.state = 'cancel'

    def action_to_draft(self):
        self.state = 'draft'

    def action_print(self):
        self.ensure_one()
        model_name = \
            "l10n_ve_vat_ledger.action_account_vat_ledger_report_xlsx"
        self.env.ref(model_name).report_file = self.display_name

        return self.env.ref(model_name).report_action(self)
