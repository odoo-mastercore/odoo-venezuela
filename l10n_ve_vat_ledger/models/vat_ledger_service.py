# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2026-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round


class L10nVeVatLedgerService(models.AbstractModel):
    _name = 'l10n_ve.vat.ledger.service'
    _description = 'Venezuela VAT Ledger Service'

    _LEDGER_MOVE_TYPES = {
        'sale': ('out_invoice', 'out_refund'),
        'purchase': ('in_invoice', 'in_refund'),
    }

    _TRACKED_RATES = {
        16.0: ('base_16', 'tax_16'),
        8.0: ('base_8', 'tax_8'),
        15.0: ('base_15', 'tax_15'),
    }

    _SALE_NUMERIC_FIELDS = (
        'amount_total',
        'third_exempt', 'third_base', 'third_tax',
        'contrib_exempt', 'contrib_base_16', 'contrib_tax_16', 'contrib_base_8', 'contrib_tax_8', 'contrib_base_15', 'contrib_tax_15',
        'non_contrib_exempt', 'non_contrib_base_16', 'non_contrib_tax_16', 'non_contrib_base_8', 'non_contrib_tax_8', 'non_contrib_base_15', 'non_contrib_tax_15',
        'withholding', 'igtf',
        # Compatibilidad con wizard piloto
        'base_16', 'tax_16', 'base_8', 'tax_8', 'base_15', 'tax_15', 'exempt',
    )

    _PURCHASE_NUMERIC_FIELDS = (
        'amount_total', 'purchase_no_credit',
        'import_base', 'import_tax',
        'internal_base_16', 'internal_tax_16',
        'internal_base_8', 'internal_tax_8',
        'internal_base_15', 'internal_tax_15',
        'withholding', 'igtf',
        # Compatibilidad con wizard piloto
        'base_16', 'tax_16', 'base_8', 'tax_8', 'base_15', 'tax_15', 'exempt',
    )

    @api.model
    def build_ledger_data(self, ledger_type, options):
        if ledger_type not in self._LEDGER_MOVE_TYPES:
            raise UserError(_('Tipo de libro inválido: %s') % ledger_type)

        normalized = self._normalize_options(ledger_type, options or {})
        move_domain = self._get_move_domain(ledger_type, normalized)
        moves = self.env['account.move'].search(move_domain, order='invoice_date, date, id')

        withholding_map = self._get_withholding_amount_by_move(ledger_type, normalized)
        numeric_fields = self._SALE_NUMERIC_FIELDS if ledger_type == 'sale' else self._PURCHASE_NUMERIC_FIELDS

        lines = []
        totals = defaultdict(float)
        for sequence, move in enumerate(moves, start=1):
            tax_buckets = self._compute_tax_buckets(move)
            sign = self._get_sign(move)
            move_total = abs(move.amount_total_signed or move.amount_total or 0.0)
            withholding_amount = withholding_map.get(move.id, 0.0)
            invoice_date = self._get_invoice_date(move, ledger_type)

            line_vals = {
                'sequence': sequence,
                'move_id': move.id,
                'invoice_date': invoice_date,
                'doc_type': self._get_doc_type_label(move),
                'note_type': self._get_note_type(move),  # compatibilidad wizard
                'document_number': self._get_document_number(move, ledger_type),
                'move_name': move.name,
                'move_ref': move.ref,
                'control_number': move.l10n_ve_control_number or '',
                'receipt_number': '',
                'affected_document': self._get_affected_document(move),
                'import_sheet_number': '',
                'import_file_number': '',
                'partner_name': move.commercial_partner_id.display_name,
                'partner_vat': self._format_partner_vat(move.commercial_partner_id),
                'amount_total': sign * move_total,
                'withholding': sign * withholding_amount,
                'igtf': sign * self._get_igtf_amount(move, ledger_type),
                # compatibilidad wizard
                'base_16': sign * tax_buckets['base_16'],
                'tax_16': sign * tax_buckets['tax_16'],
                'base_8': sign * tax_buckets['base_8'],
                'tax_8': sign * tax_buckets['tax_8'],
                'base_15': sign * tax_buckets['base_15'],
                'tax_15': sign * tax_buckets['tax_15'],
                'exempt': sign * tax_buckets['exempt'],
            }

            if ledger_type == 'sale':
                self._fill_sale_columns(line_vals, tax_buckets, sign, move)
            else:
                self._fill_purchase_columns(line_vals, tax_buckets, sign)

            lines.append(line_vals)
            for key in numeric_fields:
                totals[key] += line_vals.get(key, 0.0)

        return {
            'header': {
                'ledger_type': ledger_type,
                'ledger_name': _('Libro IVA Ventas') if ledger_type == 'sale' else _('Libro IVA Compras'),
                'company_id': normalized['company'].id,
                'company_name': normalized['company'].display_name,
                'date_from': normalized['date_from'],
                'date_to': normalized['date_to'],
                'journal_ids': normalized['journals'].ids,
                'journal_names': ', '.join(normalized['journals'].mapped('display_name')),
                'numeric_fields': list(numeric_fields),
            },
            'lines': lines,
            'totals': dict(totals),
            'warnings': [],
        }

    @api.model
    def _fill_sale_columns(self, line_vals, tax_buckets, sign, move):
        is_contributor = bool(move.partner_id.l10n_latam_identification_type_id.is_vat)
        exento = sign * tax_buckets['exempt']
        base_16 = sign * tax_buckets['base_16']
        tax_16 = sign * tax_buckets['tax_16']
        base_8 = sign * tax_buckets['base_8']
        tax_8 = sign * tax_buckets['tax_8']
        base_15 = sign * tax_buckets['base_15']
        tax_15 = sign * tax_buckets['tax_15']

        line_vals.update({
            # Ventas por cuenta de terceros (se mantiene estructura original)
            'third_exempt': 0.0,
            'third_base': 0.0,
            'third_rate': '',
            'third_tax': 0.0,
            # Contribuyente
            'contrib_exempt': exento if is_contributor else 0.0,
            'contrib_base_16': base_16 if is_contributor else 0.0,
            'contrib_rate_16': '16%' if is_contributor and base_16 else '',
            'contrib_tax_16': tax_16 if is_contributor else 0.0,
            'contrib_base_8': base_8 if is_contributor else 0.0,
            'contrib_rate_8': '8%' if is_contributor and base_8 else '',
            'contrib_tax_8': tax_8 if is_contributor else 0.0,
            'contrib_base_15': base_15 if is_contributor else 0.0,
            'contrib_rate_15': '15%' if is_contributor and base_15 else '',
            'contrib_tax_15': tax_15 if is_contributor else 0.0,
            # No Contribuyente
            'non_contrib_exempt': exento if not is_contributor else 0.0,
            'non_contrib_base_16': base_16 if not is_contributor else 0.0,
            'non_contrib_rate_16': '16%' if (not is_contributor and base_16) else '',
            'non_contrib_tax_16': tax_16 if not is_contributor else 0.0,
            'non_contrib_base_8': base_8 if not is_contributor else 0.0,
            'non_contrib_rate_8': '8%' if (not is_contributor and base_8) else '',
            'non_contrib_tax_8': tax_8 if not is_contributor else 0.0,
            'non_contrib_base_15': base_15 if not is_contributor else 0.0,
            'non_contrib_rate_15': '15%' if (not is_contributor and base_15) else '',
            'non_contrib_tax_15': tax_15 if not is_contributor else 0.0,
        })

    @api.model
    def _fill_purchase_columns(self, line_vals, tax_buckets, sign):
        exento = sign * tax_buckets['exempt']
        base_16 = sign * tax_buckets['base_16']
        tax_16 = sign * tax_buckets['tax_16']
        base_8 = sign * tax_buckets['base_8']
        tax_8 = sign * tax_buckets['tax_8']
        base_15 = sign * tax_buckets['base_15']
        tax_15 = sign * tax_buckets['tax_15']

        line_vals.update({
            'purchase_no_credit': exento,
            'import_base': 0.0,
            'import_rate': '',
            'import_tax': 0.0,
            'internal_base_16': base_16,
            'internal_rate_16': '16%' if base_16 else '',
            'internal_tax_16': tax_16,
            'internal_base_8': base_8,
            'internal_rate_8': '8%' if base_8 else '',
            'internal_tax_8': tax_8,
            'internal_base_15': base_15,
            'internal_rate_15': '15%' if base_15 else '',
            'internal_tax_15': tax_15,
        })

    @api.model
    def _normalize_options(self, ledger_type, options):
        date_from = fields.Date.to_date(options.get('date_from') or options.get('date', {}).get('date_from'))
        date_to = fields.Date.to_date(options.get('date_to') or options.get('date', {}).get('date_to'))
        today = fields.Date.context_today(self)
        if not date_from:
            date_from = today.replace(day=1)
        if not date_to:
            date_to = today

        company_ids = options.get('company_ids') or options.get('allowed_company_ids')
        if not company_ids and options.get('companies'):
            company_ids = [company['id'] for company in options['companies']]
        if not company_ids and options.get('company_id'):
            company_value = options['company_id']
            company_ids = [company_value.id] if hasattr(company_value, 'id') else [company_value]
        if not company_ids:
            company_ids = [self.env.company.id]

        company_ids = [company_id for company_id in company_ids if company_id]
        if len(company_ids) == 1 and options.get('include_child_companies', True):
            company_ids = self.env['res.company'].search([('id', 'child_of', company_ids)]).ids

        company = self.env['res.company'].browse(company_ids[0]) if company_ids else self.env.company
        journals = self._resolve_journals(ledger_type, options, company_ids)

        return {
            'company': company,
            'company_ids': company_ids,
            'date_from': date_from,
            'date_to': date_to,
            'journals': journals,
            'all_entries': bool(options.get('all_entries')),
        }

    @api.model
    def _resolve_journals(self, ledger_type, options, company_ids):
        journal_type = 'sale' if ledger_type == 'sale' else 'purchase'
        journal_ids = []

        raw_journal_ids = options.get('journal_ids')
        if raw_journal_ids:
            if hasattr(raw_journal_ids, 'ids'):
                journal_ids = raw_journal_ids.ids
            else:
                journal_ids = [jid for jid in raw_journal_ids if isinstance(jid, int)]

        if not journal_ids and options.get('journals'):
            journal_options = [journal for journal in options['journals'] if journal.get('model') == 'account.journal']
            selected = [journal['id'] for journal in journal_options if journal.get('selected')]
            journal_ids = selected or [journal['id'] for journal in journal_options]

        if journal_ids:
            journals = self.env['account.journal'].search([
                ('id', 'in', journal_ids),
                ('company_id', 'in', company_ids),
                ('type', '=', journal_type),
            ])
        else:
            journals = self.env['account.journal'].search([
                ('company_id', 'in', company_ids),
                ('type', '=', journal_type),
            ])

        return journals

    @api.model
    def _get_move_domain(self, ledger_type, normalized):
        domain = [
            ('company_id', 'in', normalized['company_ids']),
            ('journal_id', 'in', normalized['journals'].ids),
            ('move_type', 'in', self._LEDGER_MOVE_TYPES[ledger_type]),
            ('state', '=', 'posted') if not normalized['all_entries'] else ('state', '!=', 'cancel'),
        ]

        if ledger_type == 'sale':
            domain.extend([
                ('l10n_ve_control_number', '!=', False),
                ('name', '!=', False),
                ('invoice_date', '>=', normalized['date_from']),
                ('invoice_date', '<=', normalized['date_to']),
            ])
        else:
            domain.extend([
                ('date', '>=', normalized['date_from']),
                ('date', '<=', normalized['date_to']),
            ])

        return domain

    @api.model
    def _compute_tax_buckets(self, move):
        result = {
            'base_16': 0.0,
            'tax_16': 0.0,
            'base_8': 0.0,
            'tax_8': 0.0,
            'base_15': 0.0,
            'tax_15': 0.0,
            'exempt': 0.0,
        }

        # Importante: las líneas de impuesto tienen display_type='tax'.
        tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id)
        for tax_line in tax_lines:
            rate = abs(float_round(tax_line.tax_line_id.amount or 0.0, precision_digits=2))
            base_amount = abs(tax_line.tax_base_amount or 0.0)
            tax_amount = abs(tax_line.balance or 0.0)

            if self._is_zero_rate(rate):
                result['exempt'] += base_amount
                continue

            rate_match = self._match_supported_rate(rate)
            if not rate_match:
                continue

            base_key, tax_key = self._TRACKED_RATES[rate_match]
            result[base_key] += base_amount
            result[tax_key] += tax_amount

        if not any(result.values()):
            exempt_base = 0.0
            for invoice_line in move.invoice_line_ids.filtered(lambda line: not line.display_type):
                if not invoice_line.tax_ids or all(self._is_zero_rate(tax.amount) for tax in invoice_line.tax_ids):
                    exempt_base += abs(invoice_line.price_subtotal)
            result['exempt'] = exempt_base

        return result

    @api.model
    def _get_withholding_amount_by_move(self, ledger_type, normalized):
        result = defaultdict(float)
        withholdings = self.env['l10n_ve.payment.withholding'].search(self._get_withholding_domain(ledger_type, normalized))
        move_types = self._LEDGER_MOVE_TYPES[ledger_type]

        for withholding in withholdings:
            tax_lines = withholding.l10n_ve_move_line_taxes_ids.filtered(
                lambda line: (
                    line.move_id
                    and line.move_id.move_type in move_types
                    and line.move_id.company_id.id in normalized['company_ids']
                    and line.move_id.journal_id.id in normalized['journals'].ids
                )
            )
            if not tax_lines:
                continue

            weighted_tax_total = sum(abs(line.balance or 0.0) for line in tax_lines)
            use_equal_distribution = not weighted_tax_total

            for line in tax_lines:
                if use_equal_distribution:
                    line_weight = 1.0 / len(tax_lines)
                elif len(tax_lines) > 1:
                    line_weight = abs(line.balance or 0.0) / weighted_tax_total
                else:
                    line_weight = 1.0
                result[line.move_id.id] += withholding.amount * line_weight

        return result

    @api.model
    def _get_withholding_domain(self, ledger_type, normalized):
        domain = [
            ('company_id', 'in', normalized['company_ids']),
            ('payment_id.state', 'in', ['in_process', 'paid']),
            ('date', '>=', normalized['date_from']),
            ('date', '<=', normalized['date_to']),
        ]

        if ledger_type == 'sale':
            domain.extend([
                ('tax_id.l10n_ve_withholding_payment_type', '=', 'customer'),
                ('tax_id.l10n_ve_withholding_ingoing_type', '=', 'iva'),
            ])
        else:
            domain.extend([
                ('tax_id.l10n_ve_withholding_payment_type', '=', 'supplier'),
            ])

        return domain

    @api.model
    def _get_sign(self, move):
        return -1.0 if move.move_type in ('out_refund', 'in_refund') else 1.0

    @api.model
    def _get_note_type(self, move):
        if move.move_type in ('out_refund', 'in_refund'):
            return 'credit'
        if move.debit_origin_id:
            return 'debit'
        return 'invoice'

    @api.model
    def _get_doc_type_label(self, move):
        if move.move_type in ('out_refund', 'in_refund') and not move.debit_origin_id:
            return 'Nota de Credito'
        if move.debit_origin_id:
            return 'Nota de Debito'
        return 'Factura'

    @api.model
    def _get_document_number(self, move, ledger_type):
        if ledger_type == 'sale' and hasattr(move, '_get_name_vat_ledger'):
            return move._get_name_vat_ledger() or ''
        return move.ref or move.name or ''

    @api.model
    def _get_affected_document(self, move):
        if move.move_type in ('out_refund', 'in_refund') and move.reversed_entry_id:
            return move.reversed_entry_id.name or ''
        if move.debit_origin_id:
            return move.debit_origin_id.name or ''
        return ''

    @api.model
    def _get_invoice_date(self, move, ledger_type):
        if ledger_type == 'sale':
            return move.l10n_ve_invoice_date or move.invoice_date or move.date
        return move.invoice_date or move.date

    @api.model
    def _get_igtf_amount(self, move, ledger_type):
        if ledger_type == 'purchase' and hasattr(move, '_get_igtf_amount_purchase'):
            return abs(move._get_igtf_amount_purchase() or 0.0)
        if ledger_type == 'sale' and hasattr(move, '_get_igtf_amount'):
            return abs(move._get_igtf_amount() or 0.0)
        return 0.0

    @api.model
    def _format_partner_vat(self, partner):
        if not partner:
            return ''
        prefix = partner.l10n_latam_identification_type_id.l10n_ve_code or ''
        vat = partner.vat or ''
        return '%s-%s' % (prefix, vat) if prefix or vat else ''

    @api.model
    def _match_supported_rate(self, rate):
        for supported in self._TRACKED_RATES:
            if abs(rate - supported) <= 0.001:
                return supported
        return False

    @api.model
    def _is_zero_rate(self, rate):
        return abs((rate or 0.0) - 0.0) <= 0.001
