# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2026-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, _


class L10nVeVatLedgerPilotXlsx(models.AbstractModel):
    _name = 'report.l10n_ve_vat_ledger.vat_ledger_pilot_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Venezuela VAT Ledger Pilot XLSX'

    def generate_xlsx_report(self, workbook, data, wizards):
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center'})
        text_fmt = workbook.add_format({'border': 1})
        amount_fmt = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        title_fmt = workbook.add_format({'bold': True, 'font_size': 12})

        for wizard in wizards:
            sheet_name = _('Libro IVA Ventas') if wizard.ledger_type == 'sale' else _('Libro IVA Compras')
            sheet = workbook.add_worksheet(sheet_name[:31])

            sheet.set_column(0, 0, 6)
            sheet.set_column(1, 2, 12)
            sheet.set_column(3, 6, 20)
            sheet.set_column(7, 15, 14)

            row = 0
            sheet.write(row, 0, sheet_name, title_fmt)
            row += 1
            sheet.write(row, 0, _('Compañía:'), text_fmt)
            sheet.write(row, 1, wizard.company_id.display_name, text_fmt)
            row += 1
            sheet.write(row, 0, _('Período:'), text_fmt)
            sheet.write(row, 1, '%s - %s' % (wizard.date_from or '', wizard.date_to or ''), text_fmt)
            row += 2

            headers = [
                '#', 'Fecha', 'Tipo', 'Número', 'Control', 'Partner', 'RIF',
                'Base 16%', 'IVA 16%', 'Base 8%', 'IVA 8%', 'Base 15%', 'IVA 15%',
                'Exento', 'Total', 'Retención',
            ]
            for col, header in enumerate(headers):
                sheet.write(row, col, header, header_fmt)

            row += 1
            for line in wizard.line_ids:
                sheet.write(row, 0, line.sequence, text_fmt)
                sheet.write(row, 1, str(line.invoice_date or ''), text_fmt)
                sheet.write(row, 2, dict(line._fields['note_type'].selection).get(line.note_type, ''), text_fmt)
                sheet.write(row, 3, line.move_name or '', text_fmt)
                sheet.write(row, 4, line.control_number or '', text_fmt)
                sheet.write(row, 5, line.partner_name or '', text_fmt)
                sheet.write(row, 6, line.partner_vat or '', text_fmt)
                sheet.write_number(row, 7, line.base_16 or 0.0, amount_fmt)
                sheet.write_number(row, 8, line.tax_16 or 0.0, amount_fmt)
                sheet.write_number(row, 9, line.base_8 or 0.0, amount_fmt)
                sheet.write_number(row, 10, line.tax_8 or 0.0, amount_fmt)
                sheet.write_number(row, 11, line.base_15 or 0.0, amount_fmt)
                sheet.write_number(row, 12, line.tax_15 or 0.0, amount_fmt)
                sheet.write_number(row, 13, line.exempt or 0.0, amount_fmt)
                sheet.write_number(row, 14, line.amount_total or 0.0, amount_fmt)
                sheet.write_number(row, 15, line.withholding or 0.0, amount_fmt)
                row += 1

            sheet.write(row, 6, _('Totales'), header_fmt)
            sheet.write_number(row, 7, wizard.total_base_16 or 0.0, amount_fmt)
            sheet.write_number(row, 8, wizard.total_tax_16 or 0.0, amount_fmt)
            sheet.write_number(row, 9, wizard.total_base_8 or 0.0, amount_fmt)
            sheet.write_number(row, 10, wizard.total_tax_8 or 0.0, amount_fmt)
            sheet.write_number(row, 11, wizard.total_base_15 or 0.0, amount_fmt)
            sheet.write_number(row, 12, wizard.total_tax_15 or 0.0, amount_fmt)
            sheet.write_number(row, 13, wizard.total_exempt or 0.0, amount_fmt)
            sheet.write_number(row, 14, wizard.total_amount or 0.0, amount_fmt)
            sheet.write_number(row, 15, wizard.total_withholding or 0.0, amount_fmt)
