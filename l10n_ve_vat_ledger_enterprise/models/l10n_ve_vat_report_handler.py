# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2026-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, _


class L10nVeVatReportHandler(models.AbstractModel):
    _name = 'l10n_ve.vat.report.handler'
    _inherit = 'account.tax.report.handler'
    _description = 'Venezuela VAT Report Handler'

    def _custom_options_initializer(self, report, options, previous_options):
        super()._custom_options_initializer(report, options, previous_options)
        ledger_type = self._get_ledger_type(report)
        expected_journal_type = 'sale' if ledger_type == 'sale' else 'purchase'

        for journal_option in options.get('journals', []):
            if journal_option.get('model') == 'account.journal' and journal_option.get('type') != expected_journal_type:
                journal_option['selected'] = False
                journal_option['visible'] = False

        options['forced_domain'] = [*options.get('forced_domain', []), ('journal_id.type', '=', expected_journal_type)]

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):
        ledger_type = self._get_ledger_type(report)
        service_options = self._build_service_options(report, options, ledger_type)
        ledger_data = self.env['l10n_ve.vat.ledger.service'].build_ledger_data(ledger_type, service_options)
        numeric_labels = set(ledger_data['header'].get('numeric_fields', []))

        lines = []
        for line_vals in ledger_data['lines']:
            columns = []
            for column in options['columns']:
                expression_label = column['expression_label']
                value = line_vals.get(expression_label)
                if value is None and expression_label in numeric_labels:
                    value = 0.0
                elif value is None:
                    value = ''
                columns.append(report._build_column_dict(value, column, options=options))

            lines.append((0, {
                'id': report._get_generic_line_id('account.move', line_vals['move_id']),
                'caret_options': 'account.move',
                'name': line_vals.get('document_number') or line_vals.get('move_name') or line_vals.get('move_ref') or '/',
                'level': 2,
                'columns': columns,
            }))

        totals = ledger_data['totals']
        total_columns = []
        for column in options['columns']:
            expression_label = column['expression_label']
            if expression_label in numeric_labels:
                total_columns.append(report._build_column_dict(totals.get(expression_label, 0.0), column, options=options))
            else:
                total_columns.append(report._build_column_dict('', column, options=options))

        lines.append((0, {
            'id': report._get_generic_line_id(None, None, markup='total'),
            'name': _('Total'),
            'class': 'total',
            'level': 1,
            'columns': total_columns,
        }))

        return lines

    def _build_service_options(self, report, options, ledger_type):
        company_ids = report.get_report_company_ids(options)
        journal_type = 'sale' if ledger_type == 'sale' else 'purchase'

        journal_options = [
            journal
            for journal in options.get('journals', [])
            if journal.get('model') == 'account.journal' and journal.get('type') == journal_type
        ]
        selected_journal_ids = [journal['id'] for journal in journal_options if journal.get('selected')]
        journal_ids = selected_journal_ids or [journal['id'] for journal in journal_options]

        return {
            'company_ids': company_ids,
            'include_child_companies': False,
            'date_from': options.get('date', {}).get('date_from'),
            'date_to': options.get('date', {}).get('date_to'),
            'journal_ids': journal_ids,
            'all_entries': options.get('all_entries'),
        }

    def _get_ledger_type(self, report):
        purchase_report = self.env.ref('l10n_ve_vat_ledger_enterprise.ve_vat_purchase_report', raise_if_not_found=False)
        return 'purchase' if purchase_report and report.id == purchase_report.id else 'sale'
