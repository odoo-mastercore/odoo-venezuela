# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2026-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import api, fields, models, Command, _


class L10nVeVatLedgerPilotWizard(models.TransientModel):
    _name = 'l10n_ve.vat.ledger.pilot.wizard'
    _description = 'Venezuela VAT Ledger Pilot Wizard'

    def _default_date_from(self):
        today = fields.Date.context_today(self)
        return today.replace(day=1)

    def _default_date_to(self):
        return fields.Date.context_today(self)

    def _default_ledger_type(self):
        return self.env.context.get('default_ledger_type', 'sale')

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )
    ledger_type = fields.Selection(
        [('sale', 'Ventas'), ('purchase', 'Compras')],
        string='Tipo de libro',
        required=True,
        default=_default_ledger_type,
    )
    date_from = fields.Date(
        string='Fecha inicio',
        required=True,
        default=_default_date_from,
    )
    date_to = fields.Date(
        string='Fecha fin',
        required=True,
        default=_default_date_to,
    )
    journal_ids = fields.Many2many(
        'account.journal',
        string='Diarios',
    )
    line_ids = fields.One2many(
        'l10n_ve.vat.ledger.pilot.wizard.line',
        'wizard_id',
        string='Líneas',
        copy=False,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True,
    )

    total_base_16 = fields.Monetary(compute='_compute_totals', string='Base 16%', currency_field='currency_id')
    total_tax_16 = fields.Monetary(compute='_compute_totals', string='IVA 16%', currency_field='currency_id')
    total_base_8 = fields.Monetary(compute='_compute_totals', string='Base 8%', currency_field='currency_id')
    total_tax_8 = fields.Monetary(compute='_compute_totals', string='IVA 8%', currency_field='currency_id')
    total_base_15 = fields.Monetary(compute='_compute_totals', string='Base 15%', currency_field='currency_id')
    total_tax_15 = fields.Monetary(compute='_compute_totals', string='IVA 15%', currency_field='currency_id')
    total_exempt = fields.Monetary(compute='_compute_totals', string='Exento', currency_field='currency_id')
    total_amount = fields.Monetary(compute='_compute_totals', string='Total', currency_field='currency_id')
    total_withholding = fields.Monetary(compute='_compute_totals', string='Retención', currency_field='currency_id')

    @api.depends('line_ids', 'line_ids.base_16', 'line_ids.tax_16', 'line_ids.base_8', 'line_ids.tax_8', 'line_ids.base_15', 'line_ids.tax_15', 'line_ids.exempt', 'line_ids.amount_total', 'line_ids.withholding')
    def _compute_totals(self):
        for wizard in self:
            wizard.total_base_16 = sum(wizard.line_ids.mapped('base_16'))
            wizard.total_tax_16 = sum(wizard.line_ids.mapped('tax_16'))
            wizard.total_base_8 = sum(wizard.line_ids.mapped('base_8'))
            wizard.total_tax_8 = sum(wizard.line_ids.mapped('tax_8'))
            wizard.total_base_15 = sum(wizard.line_ids.mapped('base_15'))
            wizard.total_tax_15 = sum(wizard.line_ids.mapped('tax_15'))
            wizard.total_exempt = sum(wizard.line_ids.mapped('exempt'))
            wizard.total_amount = sum(wizard.line_ids.mapped('amount_total'))
            wizard.total_withholding = sum(wizard.line_ids.mapped('withholding'))

    @api.onchange('company_id', 'ledger_type')
    def _onchange_company_or_type(self):
        journal_type = 'sale' if self.ledger_type == 'sale' else 'purchase'
        journals = self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
            ('type', '=', journal_type),
        ])
        self.journal_ids = [Command.set(journals.ids)]

    def _get_service_options(self):
        self.ensure_one()
        return {
            'company_id': self.company_id.id,
            'include_child_companies': True,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'journal_ids': self.journal_ids.ids,
        }

    def _load_preview_lines(self):
        self.ensure_one()
        data = self.env['l10n_ve.vat.ledger.service'].build_ledger_data(self.ledger_type, self._get_service_options())

        commands = [Command.clear()]
        for line in data['lines']:
            commands.append(Command.create({
                'sequence': line['sequence'],
                'move_id': line['move_id'],
                'invoice_date': line['invoice_date'],
                'move_name': line.get('move_name'),
                'move_ref': line.get('move_ref'),
                'control_number': line.get('control_number'),
                'partner_name': line.get('partner_name'),
                'partner_vat': line.get('partner_vat'),
                'note_type': line.get('note_type'),
                'base_16': line.get('base_16', 0.0),
                'tax_16': line.get('tax_16', 0.0),
                'base_8': line.get('base_8', 0.0),
                'tax_8': line.get('tax_8', 0.0),
                'base_15': line.get('base_15', 0.0),
                'tax_15': line.get('tax_15', 0.0),
                'exempt': line.get('exempt', 0.0),
                'amount_total': line.get('amount_total', 0.0),
                'withholding': line.get('withholding', 0.0),
            }))
        self.line_ids = commands

    def _reload_action(self):
        self.ensure_one()
        return {
            'name': _('Libro IVA Piloto'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_load_preview(self):
        self.ensure_one()
        self._load_preview_lines()
        return self._reload_action()

    def action_export_xlsx(self):
        self.ensure_one()
        self._load_preview_lines()
        return self.env.ref('l10n_ve_vat_ledger.action_vat_ledger_pilot_xlsx').report_action(self)

    def action_export_pdf(self):
        self.ensure_one()
        self._load_preview_lines()
        return self.env.ref('l10n_ve_vat_ledger.action_vat_ledger_pilot_pdf').report_action(self)


class L10nVeVatLedgerPilotWizardLine(models.TransientModel):
    _name = 'l10n_ve.vat.ledger.pilot.wizard.line'
    _description = 'Venezuela VAT Ledger Pilot Wizard Line'
    _order = 'sequence, invoice_date, id'

    wizard_id = fields.Many2one(
        'l10n_ve.vat.ledger.pilot.wizard',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='#')
    move_id = fields.Many2one('account.move', string='Asiento')
    invoice_date = fields.Date(string='Fecha')
    move_name = fields.Char(string='Número')
    move_ref = fields.Char(string='Referencia')
    control_number = fields.Char(string='Nro. Control')
    partner_name = fields.Char(string='Partner')
    partner_vat = fields.Char(string='RIF')
    note_type = fields.Selection(
        [('invoice', 'Factura'), ('credit', 'N/C'), ('debit', 'N/D')],
        string='Tipo',
    )
    base_16 = fields.Monetary(string='Base 16%', currency_field='currency_id')
    tax_16 = fields.Monetary(string='IVA 16%', currency_field='currency_id')
    base_8 = fields.Monetary(string='Base 8%', currency_field='currency_id')
    tax_8 = fields.Monetary(string='IVA 8%', currency_field='currency_id')
    base_15 = fields.Monetary(string='Base 15%', currency_field='currency_id')
    tax_15 = fields.Monetary(string='IVA 15%', currency_field='currency_id')
    exempt = fields.Monetary(string='Exento', currency_field='currency_id')
    amount_total = fields.Monetary(string='Total', currency_field='currency_id')
    withholding = fields.Monetary(string='Retención', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        related='wizard_id.currency_id',
        readonly=True,
    )
