##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
# import time
import logging

_logger = logging.getLogger(__name__)

class AccountVatLedgerXlsx(models.AbstractModel):

    _name = 'report.l10n_ve_vat_ledger.account_vat_ledger_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Xlsx Account VAT Ledger"

    def generate_xlsx_report(self, workbook, data, account_vat):
        for obj in account_vat:
            report_name = obj.name
            sheet = workbook.add_worksheet(report_name[:31])
            title = workbook.add_format({'bold': True})
            bold = workbook.add_format({'bold': True, 'border':1})
            line = workbook.add_format({'border': 1})
            date_line = workbook.add_format(
                {'border': 1, 'num_format': 'dd-mm-yyyy'})
            sheet.set_column(0, 0, 9)
            sheet.set_column(1, 4, 20)
            sheet.set_column(5, 10, 13)
            sheet.set_column(11, 14, 24)
            

            #
            sheet.write(0, 0, obj.company_id.name, title)
            sheet.write(1, 0, obj.company_id.vat, title)
            sheet.write(2, 0, obj.name, title)

            sheet.write(4, 0, 'Nro Oper.', bold)
            sheet.write(4, 1, 'Fecha de la Factura', bold)
            sheet.write(4, 2, 'Número Factura', bold)
            sheet.write(4, 3, 'Número de Control', bold)
            sheet.write(4, 4, 'Nombre', bold)
            sheet.write(4, 5, 'RIF', bold)
            sheet.write(4, 6, 'Número Nota de Credito', bold)
            sheet.write(4, 7, 'Número Nota de Debito', bold)
            sheet.write(4, 8, 'Número Fact. Afect', bold)
            sheet.write(4, 9, 'Tipo de Trans.', bold)
            sheet.write(4, 10, '% ALic.', bold)
            sheet.write(4, 11, 'Base Imponible', bold)
            sheet.write(4, 12, 'Impuesto IVA.', bold)
            sheet.write(4, 13, 'Total Ventas Incluyendo IVA.', bold)
            sheet.write(4, 14, 'Total Ventas Internas No Gravadas.', bold)

            row = 5
            total_amount_taxed = 0
            total_amount_untaxed = 0
            total_amount = 0
            total_amount_other_tax = 0
            i = 0   
            for invoice in obj.invoice_ids:
                if obj.type == 'purchase':
                    # Write Purchase lines 
                    i += 1
                    sheet.write(row, 0, i, line)
                    sheet.write(row, 1, invoice.invoice_date, date_line)
                    sheet.write(row, 2, invoice.ref, line)
                    sheet.write(row, 3, invoice.l10n_ve_document_number, line)
                    sheet.write(row, 4, invoice.partner_id.name, line)
                    sheet.write(row, 5, invoice.partner_id.\
                        l10n_latam_identification_type_id.l10n_ve_code+'-'+
                        invoice.partner_id.vat, line)
                    sheet.write(row, 6, '', line)
                    sheet.write(row, 7, '', line)
                    sheet.write(row, 8, '', line)
                    sheet.write(row, 9, '01-REG', line)
                    sheet.write(row, 10, int((str(
                        invoice.amount_by_group[0][0]).replace("IVA ","")).\
                        replace("%","")), line)
                    sheet.write(row, 11, 
                        str(invoice.amount_untaxed_signed * -1), line)
                    if invoice.amount_tax_signed == 0:
                        sheet.write(row, 12, 
                            str(invoice.amount_tax_signed * -1), line)
                        sheet.write(row, 13, 0, line)
                        sheet.write(row, 14, 
                            str(invoice.amount_total_signed * -1), line)
                        total_amount_other_tax += invoice.amount_total_signed
                    else:
                        sheet.write(row, 12, 
                            str(invoice.amount_tax_signed * -1), line)
                        sheet.write(row, 13, 
                            str(invoice.amount_total_signed * -1), line)
                        sheet.write(row, 14, 0, line)
                    
                    # Adding totals
                    total_amount_taxed += invoice.amount_tax_signed * -1
                    total_amount_untaxed += invoice.amount_untaxed_signed * -1
                    total_amount += invoice.amount_total_signed * -1
                    row += 1

                elif obj.type == 'sale':
                    # Write Sale lines
                    i += 1
                    sheet.write(row, 0, i, line)
                    sheet.write(row, 1, invoice.invoice_date, date_line)
                    sheet.write(row, 2, invoice.name, line)
                    sheet.write(row, 3, invoice.l10n_ve_document_number or 'FALSE', line)
                    sheet.write(row, 4, invoice.partner_id.name or 'FALSE', line)
                    if invoice.partner_id.\
                        l10n_latam_identification_type_id.l10n_ve_code and invoice.\
                            partner_id.vat:
                        sheet.write(row, 5, invoice.partner_id.\
                            l10n_latam_identification_type_id.l10n_ve_code+'-'+invoice.\
                            partner_id.vat, line)
                    elif invoice.partner_id.\
                        l10n_latam_identification_type_id.l10n_ve_code:
                        sheet.write(row, 5, invoice.partner_id.\
                            l10n_latam_identification_type_id.l10n_ve_code+'-'+'FALSE', line)
                    else:
                        sheet.write(row, 5, 'FALSE'+'-'+invoice.partner_id.vat, line)
                    sheet.write(row, 6, '', line)
                    sheet.write(row, 7, '', line)
                    sheet.write(row, 8, '', line)
                    sheet.write(row, 9, '01-REG', line)
                    sheet.write(row, 10, int((str(
                        invoice.amount_by_group[0][0]).replace("IVA ","")).\
                        replace("%","")), line)
                    sheet.write(row, 11, invoice.amount_untaxed_signed, line)
                    if invoice.amount_tax_signed == 0:
                        sheet.write(row, 12, invoice.amount_tax_signed, line)
                        sheet.write(row, 13, 0, line)
                        sheet.write(row, 14, invoice.amount_total_signed, line)
                        total_amount_other_tax += invoice.amount_total_signed
                    else:
                        sheet.write(row, 12, invoice.amount_tax_signed, line)
                        sheet.write(row, 13, invoice.amount_total_signed, line)
                        sheet.write(row, 14, 0, line)
                    
                    # Adding totals
                    total_amount_taxed += invoice.amount_tax_signed
                    total_amount_untaxed += invoice.amount_untaxed_signed 
                    total_amount += invoice.amount_total_signed
                    row += 1

            # # Write totals lines
            sheet.write(row, 10, 'TOTALES', bold)
            sheet.write(row, 11, total_amount_untaxed, bold)
            sheet.write(row, 12, total_amount_taxed, bold)
            sheet.write(row, 13, total_amount, bold)
            sheet.write(row, 14, total_amount_other_tax, bold)