# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
from odoo.tools import format_date
import logging

_logger = logging.getLogger(__name__)



class AccountVatLedger(models.Model):

    _name = "account.vat.ledger"
    _description = "Account VAT Ledger"
    _inherit = ['mail.thread']
    _order = 'date_from desc'

    _date_range_check = models.Constraint(
        'CHECK (date_from <= date_to)',
        'La fecha de inicio debe ser anterior a la fecha de fin.',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    type = fields.Selection(
        [('sale', 'Sale'), ('purchase', 'Purchase')],
        "Type",
        required=True
    )
    date_from = fields.Date(
        string='Start Date',
        required=True,
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
    )
    journal_ids = fields.Many2many(
        'account.journal', 'account_vat_ledger_journal_rel',
        'vat_ledger_id', 'journal_id',
        string='Journals',
        required=True,
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
    withholding_ids = fields.Many2many(
        'l10n_ve.payment.withholding',
        string="Withholdings",
        compute="_compute_invoices",
        store=True
    )

    @api.depends('journal_ids', 'date_from', 'date_to', 'company_id', 'type')
    def _compute_invoices(self):
        for rec in self:
            company_ids = [rec.company_id.id]
            if rec.company_id.child_ids:
                company_ids += rec.company_id.child_ids.ids
            invoices_domain = [
                ('state', 'not in', ['draft']),
                ('journal_id', 'in', rec.journal_ids.ids),
                ('company_id', 'in', company_ids),
            ]
            withholdings_domain = [
                ('payment_id.state', 'in', ['in_process', 'paid']),
                ('company_id', 'in', company_ids),
            ]
            if rec.type == 'sale':
                invoices_domain += [
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('l10n_ve_control_number', '!=', False),
                    ('name', '!=', False),
                    ('invoice_date', '>=', rec.date_from),
                    ('invoice_date', '<=', rec.date_to),
                ]
                withholdings_domain += [
                    ('tax_id.l10n_ve_withholding_payment_type', '=', 'customer'),
                    ('tax_id.l10n_ve_withholding_ingoing_type', '=', 'iva'),
                    # Include withholdings by their own date or by payment date.
                    # This covers cases where withholding date and payment date differ.
                    '|',
                    '&',
                    ('date', '>=', rec.date_from),
                    ('date', '<=', rec.date_to),
                    '&',
                    ('payment_id.date', '>=', rec.date_from),
                    ('payment_id.date', '<=', rec.date_to),
                ]
            elif rec.type == 'purchase':
                invoices_domain += [
                    ('move_type', 'in', ['in_invoice', 'in_refund']),
                    ('date', '>=', rec.date_from),
                    ('date', '<=', rec.date_to),
                    ('state', '!=', 'cancel'),
                ]
                withholding_tax = self.env.ref('account.%s_tax_retencion_iva' % rec.company_id.id)
                withholdings_domain += [
                    ('tax_id.l10n_ve_withholding_payment_type', '=', 'supplier'),
                    ('tax_id', '=', withholding_tax.id),
                    ('date', '>=', rec.date_from),
                    ('date', '<=', rec.date_to),
                ]
            rec.invoice_ids = rec.env['account.move'].search(
                invoices_domain,
                order='invoice_date desc, l10n_ve_control_number desc'
            )
            rec.withholding_ids = rec.env['l10n_ve.payment.withholding'].search(
                withholdings_domain,
                order='name desc'
            )
            
    @api.depends('type', 'reference')
    def _compute_name(self):
        for rec in self:
            if rec.type == 'sale':
                ledger_type = _('Ventas')
            elif rec.type == 'purchase':
                ledger_type = _('Compras')
            # Usar format_date para aplicar localización
            if rec.date_from and rec.date_to:
                name = _("Libro IVA ({0})  {1} - {2}").format(
                    ledger_type,
                    format_date(self.env, rec.date_from),
                    format_date(self.env, rec.date_to),
                )
            else:
                name = _("Libro IVA (%s)") % (ledger_type,)
            rec.name = name

 

    @api.onchange('company_id', 'type')
    def change_company(self):
        self.ensure_one()
        domain = []
        if self.type == 'sale':
            domain.append(('type', '=', 'sale'))
        elif self.type == 'purchase':
            domain.append(('type', '=', 'purchase'))
        if self.company_id.child_ids:
            domain.extend([
                '|',
                ('company_id', 'in', self.company_id.child_ids.ids),
                ('company_id', '=', self.company_id.id)
            ])
        else:
            domain.append(('company_id', '=', self.company_id.id))
        journals = self.env['account.journal'].search(domain)
        self.journal_ids = [(6, 0, journals.ids)]

    def action_present(self):
        self.write({'state': 'presented'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_to_draft(self):
        self.write({'state': 'draft'})

    def action_print(self):
        self.ensure_one()
        model_name = \
            "l10n_ve_vat_ledger.action_account_vat_ledger_report_xlsx"
        report = self.env.ref(model_name)
        return report.report_action(self, data={'report_file': self.display_name})
