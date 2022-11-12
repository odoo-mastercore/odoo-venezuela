##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from re import search
from datetime import datetime, timedelta
from odoo import models, fields, api, _
import json
# import time
import logging
import xlsxwriter
import shutil
import base64
import csv
import xlwt

_logger = logging.getLogger(__name__)

class AccountVatLedgerXlsx(models.AbstractModel):
    _name = 'report.l10n_ve_vat_ledger.account_vat_ledger_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Xlsx Account VAT Ledger"



    def find_values(self, id, json_repr):
        results = []

        def _decode_dict(a_dict):
            try:
                results.append(a_dict[id])
            except KeyError:
                pass
            return a_dict
        # Return value ignored.
        json.loads(json_repr, object_hook=_decode_dict)
        return results


    def generate_xlsx_report(self, workbook, data, account_vat):
        for obj in account_vat:
            report_name = obj.name
            print(report_name)
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True, 'border':1})

            # style nuevo
            cell_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#a64d79',
                'font_color': 'white',
                'text_wrap': 1})

            cell_format_1 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'fg_color': '#a64d79',
                'font_color': 'white'})

            cell_format_2 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'left',
                'fg_color': '#a64d79',
                'font_color': 'white'})

            title = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'})

            title_style = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'left'})

            line = workbook.add_format({
                'border': 1,
                'align': 'center'})

            date_line = workbook.add_format(
                {'border': 1, 'num_format': 'dd-mm-yyyy',
                 'align': 'center'})

            sheet.set_column(0, 0, 9)
            sheet.set_column(1, 4, 20)
            sheet.set_column(5, 10, 13)
            sheet.set_column(11, 14, 24)

            # Establece el ancho de la columna A en 30
            sheet.set_column(5, 5, 30)
            sheet.set_column(5, 6, 30)
            sheet.set_column(5, 7, 30)
            sheet.set_column(5, 8, 30)
            sheet.set_column(5, 9, 30)
            sheet.set_column(5, 11, 30)
            sheet.set_column(5, 12, 30)
            sheet.set_column(5, 13, 30)
            sheet.set_column(5, 14, 30)
            sheet.set_column(5, 15, 30)
            sheet.set_column(5, 16, 30)
            sheet.set_column(5, 17, 30)
            sheet.set_column(5, 18, 30)
            sheet.set_column(5, 19, 30)
            sheet.set_column(5, 20, 30)
            sheet.set_column(5, 21, 30)
            sheet.set_column(5, 22, 30)
            sheet.set_column(5, 23, 30)
            sheet.set_column(5, 24, 30)
            sheet.set_column(5, 25, 30)
            sheet.set_column(5, 26, 30)
            sheet.set_column(5, 27, 30)
            sheet.set_column(5, 28, 30)
            sheet.set_column(5, 29, 30)
# _____________________________________________________________________________________
# _____________________________________________________________________________________
            if obj.type == 'purchase':
                sheet.merge_range('A1:D1', obj.company_id.name,title_style)
                sheet.merge_range('A2:D2', obj.company_id.vat, title_style)
                sheet.merge_range('A3:G3', obj.name + ' ' + 'Libro de IVA Compras' + ' ' + 'mes' + ' ' + 'Año', title_style)

                # alto de las celdas
                sheet.set_row(4, 30)

                sheet.write(4, 0, 'Nro Oper.', cell_format)
                sheet.write(4, 1, 'Fecha de la Factura', cell_format)
                sheet.write(4, 2, 'Tipo de Documento', cell_format)
                sheet.write(4, 3, 'Número de Documento', cell_format)
                sheet.write(4, 4, 'Número de Control', cell_format)
                sheet.write(4, 5, 'Número Factura Afectada', cell_format)
                sheet.write(4, 6, 'Nombre o Razón Social', cell_format)
                sheet.write(4, 7, 'RIF', cell_format)
                sheet.write(4, 8, 'Tipo Proveedor', cell_format)
                sheet.write(4, 9, '% ALic.', cell_format)
                sheet.write(4, 10, 'Base Imponible Bs.', cell_format)
                sheet.write(4, 11, 'Impuesto IVA Bs.', cell_format)
                sheet.write(4, 12, 'Total Compras  Bs. Incluyendo IVA.', cell_format)
                sheet.write(4, 13, 'Compras no Sujetas ', cell_format)
                sheet.write(4, 14, 'Compras sin Derecho a Crédito I.V.A.  ', cell_format)
                sheet.write(4, 15, 'Base Imponible  ', cell_format)
                sheet.write(4, 16, '% Alic.  ', cell_format)
                sheet.write(4, 17, 'Impuesto I.V.A  ', cell_format)

                # celda adicional compras por cuenta de terceros
                sheet.merge_range('S4:T4', 'Inform. de Compras con Cred. Fisc. NO Deduc. (Art. 33)', cell_format)
                sheet.write(4, 18, 'B. Imponible ', cell_format)
                sheet.write(4, 19, 'Imp. I.V.A.', cell_format)

                #celda adicional Contribuyente
                sheet.merge_range('U4:V4', 'Inform. de Compras con Cred. Fisc. Total. Deduc. (Art. 34)', cell_format)
                sheet.write(4, 20, 'B. Imponible ', cell_format)
                sheet.write(4, 21, 'Imp. I.V.A.', cell_format)

                # celda adicional No Contibuyente
                sheet.merge_range('W4:X4', 'Inform. de Compras con Cred. Fisc. Suj. Prorrateo (Art. 34)', cell_format)
                sheet.write(4, 22, 'B. Imponible ', cell_format)
                sheet.write(4, 23, 'Imp. I.V.A.', cell_format)

                # celda adicional No Contibuyente
                # sheet.merge_range('Y4:Z4', 'Retención IVA', cell_format)
                sheet.write(4, 24, 'I.V.A Retenido', cell_format)
                sheet.write(4, 25, 'Fecha de la factura afectada', cell_format)
                sheet.write(4, 26, 'I.G.T.F Pagado  ', cell_format)
                sheet.write(4, 27, 'I.V.A. Retenido por el comprador', cell_format)
                sheet.write(4, 28, 'Anticipo de I.V.A. (importación)', cell_format)


            elif obj.type == 'sale':
                sheet.merge_range('A1:D1', obj.company_id.name, title_style)
                # sheet.merge_range('E2:S2', 'LIBRO DE VENTAS (FECHA DESDE:' + ' ' + str(obj.date_from) + ' ' + 'HASTA:' + ' ' + str(obj.date_from) + ')', title)
                # print(obj.date_from)
                sheet.merge_range('A2:D2', obj.company_id.vat, title_style)
                sheet.merge_range('A3:G3', obj.name + ' ' + 'Libro de IVA Ventas' + ' ' + 'mes' + ' ' + 'Año',
                                  title_style)

                # alto de las celdas
                sheet.set_row(4, 30)

                sheet.write(4, 0, 'Nro Oper.', cell_format)
                sheet.write(4, 1, 'Fecha de la Factura', cell_format)
                sheet.write(4, 2, 'Tipo de Documento', cell_format)
                sheet.write(4, 3, 'Número de Documento', cell_format)
                sheet.write(4, 4, 'Número de Control', cell_format)
                sheet.write(4, 5, 'Número Factura Afectada', cell_format)
                sheet.write(4, 6, 'Nombre o Razón Social', cell_format)
                sheet.write(4, 7, 'RIF', cell_format)
                sheet.write(4, 8, '% ALic.', cell_format)
                sheet.write(4, 9, 'Base Imponible Bs.', cell_format)
                sheet.write(4, 10, 'Impuesto IVA Bs.', cell_format)
                sheet.write(4, 11, 'Total Ventas  Bs. Incluyendo IVA.', cell_format)

                # celda adicional Ventas por cuenta de terceros
                sheet.merge_range('M4:P4', 'Ventas por cuenta de terceros', cell_format)
                sheet.write(4, 12, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 13, 'Base Imponible', cell_format)
                sheet.write(4, 14, '% Alic.', cell_format)
                sheet.write(4, 15, 'Impuesto I.V.A', cell_format)

                # celda adicional Contribuyente
                sheet.merge_range('Q4:T4', 'Contribuyente', cell_format)
                sheet.write(4, 16, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 17, 'Base Imponible', cell_format)
                sheet.write(4, 18, '% Alic.', cell_format)
                sheet.write(4, 19, 'Impuesto I.V.A', cell_format)

                # celda adicional No Contibuyente
                sheet.merge_range('U4:X4', 'No Contibuyente', cell_format)
                sheet.write(4, 20, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 21, 'Base Imponible', cell_format)
                sheet.write(4, 22, '% Alic.', cell_format)
                sheet.write(4, 23, 'Impuesto I.V.A', cell_format)

                # celda adicional No Contibuyente
                sheet.merge_range('Y4:Z4', 'Retención IVA', cell_format)
                sheet.write(4, 24, 'N° comprobante', cell_format)
                sheet.write(4, 25, 'I.V.A Retenido', cell_format)
                sheet.write(4, 26, 'Fecha de la factura afectada', cell_format)
                sheet.write(4, 27, 'I.G.T.F Percibido', cell_format)

            row = 5
            total_amount_taxed = 0
            total_amount_untaxed = 0
            total_amount = 0
            total_amount_other_tax = 0
            total_retencion = 0
            i = 0

            for invoice in reversed(obj.invoice_ids):
                # if obj.type == 'sale':
                # Write Sale lines
                i += 1
                # contador de la factura
                sheet.write(row, 0, i, line)
                # codigo fecha
                sheet.write(row, 1, invoice.invoice_date or 'FALSE', date_line)
                # tipo de documento
                sheet.write(row, 2, 'Tipo de factura', line)
                # Número de Documento
                sheet.write(row, 3, invoice.display_name or 'FALSE', line)
                # Número de Control
                sheet.write(row, 4, invoice.l10n_ve_document_number or 'FALSE', line)
                # Número Factura Afectada si es de debito o credito
                sheet.write(row, 5, 'Numero de factura afectada', line)
                # nombre del partner
                sheet.write(row, 6, invoice.partner_id.name or 'FALSE', line)
                # Rif del cliente
                sheet.write(row, 7, '%s-%s' % (invoice.partner_id. \
                                               l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                                               invoice.partner_id.vat or 'FALSE'), line)

                if invoice.amount_tax_signed == 0:
                    sheet.write(row, 8, 'Exento', line)
                    # base imponible
                    sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                    # Impuesto IVA Bs.
                    sheet.write(row, 10, invoice.amount_tax_signed, line)
                    # Total Ventas Bs.Incluyendo IVA
                    sheet.write(row, 11, invoice.amount_total_signed, line)
                else:
                    sheet.write(row, 8, '16%', line)
                    sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                    # Impuesto IVA Bs.
                    sheet.write(row, 10, invoice.amount_tax_signed, line)
                    # Total Ventas Bs.Incluyendo IVA
                    sheet.write(row, 11, invoice.amount_total_signed, line)

                if invoice.partner_id.l10n_latam_identification_type_id.is_vat:
                    pass
                    # # Write Purchase lines
                    # i += 1
                    # sheet.write(row, 0, i, line)
                    # sheet.write(row, 1, invoice.invoice_date or 'FALSE', date_line)
                    # sheet.write(row, 2, invoice.ref or 'FALSE', line)
                    # sheet.write(row, 3, invoice.l10n_ve_document_number or 'FALSE', line)
                    # sheet.write(row, 4, invoice.partner_id.name or 'FALSE', line)
                    # sheet.write(row, 5,  '%s-%s' %(invoice.partner_id.\
                    #     l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                    #     invoice.partner_id.vat or 'FALSE'), line)
                    # sheet.write(row, 6, '', line)
                    # sheet.write(row, 7, '', line)
                    # sheet.write(row, 8, '', line)
                    # sheet.write(row, 9, '01-REG', line)
                    # if invoice.amount_tax_signed == 0:
                    #     sheet.write(row, 10, 0, line)
                    #     sheet.write(row, 11, 0, line)
                    #     sheet.write(row, 12,
                    #         str(invoice.amount_tax_signed * -1), line)
                    #     sheet.write(row, 13, 0, line)
                    #     sheet.write(row, 14,
                    #         str(invoice.amount_total_signed * -1), line)
                    #     total_amount_other_tax += invoice.amount_total_signed
                    # else:
                    #     groups = self.find_values(
                    #         'groups_by_subtotal', invoice.tax_totals_json)
                    #     sheet.write(row, 10, int((str(
                    #         groups[0].get('Base imponible')[0].get(
                    #         'tax_group_name')).replace("IVA ", "")).replace("%", "")), line)
                    #     sheet.write(row, 11,
                    #         str(invoice.amount_untaxed_signed * -1), line)
                    #     sheet.write(row, 12,
                    #         str(invoice.amount_tax_signed * -1), line)
                    #     sheet.write(row, 13,
                    #         str(invoice.amount_total_signed * -1), line)
                    #     sheet.write(row, 14, 0, line)
                    #
                    # # Adding totals
                    # total_amount_taxed += invoice.amount_tax_signed * -1
                    # total_amount_untaxed += invoice.amount_untaxed_signed * -1
                    # total_amount += invoice.amount_total_signed * -1
                    # row += 1
# ________________________________________Ventas________________________________________________________________

                # elif obj.type == 'sale':
                #     # Write Sale lines
                #     i += 1
                #     # contador de la factura
                #     sheet.write(row, 0, i, line)
                #     # codigo fecha
                #     sheet.write(row, 1, invoice.invoice_date or 'FALSE', date_line)
                #     # tipo de documento
                #     sheet.write(row, 2, 'Tipo de factura', line)
                #     #Número de Documento
                #     sheet.write(row, 3, invoice.display_name or 'FALSE', line)
                #     #Número de Control
                #     sheet.write(row, 4, invoice.l10n_ve_document_number or 'FALSE', line)
                #     # Número Factura Afectada si es de debito o credito
                #     sheet.write(row, 5, 'Numero de factura afectada', line)
                #     #nombre del partner
                #     sheet.write(row, 6, invoice.partner_id.name or 'FALSE', line)
                #     # Rif del cliente
                #     sheet.write(row, 7,  '%s-%s' %(invoice.partner_id.\
                #         l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                #         invoice.partner_id.vat or 'FALSE'), line)
                #
                #     if invoice.amount_tax_signed == 0:
                #         sheet.write(row, 8, 'Exento', line)
                #         # base imponible
                #         sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                #         #Impuesto IVA Bs.
                #         sheet.write(row, 10, invoice.amount_tax_signed, line)
                #         # Total Ventas Bs.Incluyendo IVA
                #         sheet.write(row, 11, invoice.amount_total_signed, line)
                #     else:
                #         sheet.write(row, 8, '16%', line)
                #         sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                #         #Impuesto IVA Bs.
                #         sheet.write(row, 10, invoice.amount_tax_signed, line)
                #         # Total Ventas Bs.Incluyendo IVA
                #         sheet.write(row, 11, invoice.amount_total_signed, line)
                #
                #     if invoice.partner_id.l10n_latam_identification_type_id.is_vat:
                #         pass


                    # if invoice.amount_tax_signed != 0:
                    #     sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                    # #Impuesto IVA Bs.
                    # sheet.write(row, 10, invoice.amount_tax_signed, line)
                    # # Total Ventas Bs.Incluyendo IVA
                    # sheet.write(row, 11, invoice.amount_total_signed, line)



                    #     sheet.write(row, 10, invoice.amount_total_signed, line)
                    #     total_amount_other_tax += invoice.amount_total_signed

                    # sheet.write(row, 8, '', line)
                    # sheet.write(row, 7, '', line)
                    # sheet.write(row, 8, '', line)
                    # sheet.write(row, 9, '01-REG', line)
                    # if invoice.state == 'cancel':
                    #     sheet.write(row, 10, 0, line)
                    #     sheet.write(row, 11, 0, line)
                    #     sheet.write(row, 12, 0, line)
                    #     sheet.write(row, 13, 0, line)
                    #     sheet.write(row, 14, 0, line)
                    #     sheet.write(row, 16, 'ANULADA', line)

                    # else:
                        # if invoice.amount_tax_signed == 0:
                        #     sheet.write(row, 10, 0, line)
                        #     sheet.write(row, 11, 0, line)
                        #     sheet.write(row, 12, invoice.amount_tax_signed, line)
                        #     sheet.write(row, 13, 0, line)
                        #     sheet.write(row, 14, invoice.amount_total_signed, line)
                        #     total_amount_other_tax += invoice.amount_total_signed
                        # else:
                        #     groups = self.find_values(
                        #         'groups_by_subtotal', invoice.tax_totals_json)
                        #     # sheet.write(row, 10, int((str(
                        #     #     groups[0].get('Base imponible')[0].get(
                        #     #         'tax_group_name')).replace("IVA ", "")).
                        #     #     replace("%","")), line)
                        #     sheet.write(row, 11, invoice.amount_untaxed_signed, line)
                        #     sheet.write(row, 12, invoice.amount_tax_signed, line)
                        #     sheet.write(row, 13, invoice.amount_total_signed, line)
                        #     sheet.write(row, 14, 0, line)

                    sql = """
                    SELECT p.withholding_number AS number_wh,p.amount AS amount_wh,l.move_id AS invoice
                    FROM  account_tax AS t INNER JOIN account_payment  AS p ON t.id=p.tax_withholding_id
                    INNER JOIN account_move_line_payment_group_to_pay_rel AS g ON p.payment_group_id=g.payment_group_id
                    INNER JOIN account_move_line AS l ON g.to_pay_line_id=l.id
                    WHERE t.type_tax_use='%s' AND t.withholding_type='partner_tax' AND l.move_id=%d
                    """ % ('customer', invoice.id)
                    self._cr.execute(sql)
                    res = self._cr.fetchone()
                    reten = 0.00
                    if res:
                        reten = float(res[1])
                    else:
                        reten = 0

                    sheet.write(row, 15, reten, line)

                    # Adding totals
                    if invoice.state == 'cancel':
                        total_amount_taxed += 0
                        total_amount_untaxed += 0
                        total_amount += 0
                        total_retencion += 0
                    else:
                        total_amount_taxed += invoice.amount_tax_signed
                        total_amount_untaxed += invoice.amount_untaxed_signed
                        total_amount += invoice.amount_total_signed
                        total_retencion += reten
                        row += 1

            # if obj.type == 'sale':
            #     # RESUMEN DE LOS TOTALES VENTAS
            #     # sheet.set_row(7,50 ) altura de las celdas
            #     sheet.merge_range('J8:M8', 'RESUMEN GENERAL', cell_format_2)
            #     sheet.write(7, 13, 'Base Imponible', cell_format_1)
            #     sheet.write(7, 14, 'Débito fiscal', cell_format_1)
            #     sheet.write(7, 15, 'IVA Retenido', cell_format_1)
            #     sheet.write(7, 16, 'IGTF percibido', cell_format_1)
            #
            #     sheet.merge_range('J9:M9',  'Total Ventas Internas No Gravadas', title_style)
            #     sheet.merge_range('J10:M10', 'Total Ventas de Exportación ', title_style)
            #     sheet.merge_range('J11:M11', 'Total Ventas Internas afectadas sólo alícuota general 16.00:', title_style)
            #     sheet.merge_range('J12:M12', 'Total Ventas Internas afectadas sólo alícuota reducida 8.00:', title_style)
            #     sheet.merge_range('J13:M13', 'Total Ventas Internas afectadas por alícuota general más adicional 26.00:', title_style)
            #     sheet.merge_range('J14:M14', 'Total Notas de Crédito o Devoluciones aplicadas en Ventas:', title_style)
            #     sheet.merge_range('J15:M15', 'Total Notas de Débito o recargos aplicadas en Ventas:', title_style)
            #     sheet.merge_range('J16:M16', 'Total:', title_style)

                # 8 celda 9 columna datos de los totales
                # sheet.write(8, 9, total_amount_taxed, bold)
                # sheet.write(9, 9, total_amount, bold)
                # sheet.write(10, 9, total_amount_other_tax, bold)
                # sheet.write(15, 15, total_retencion, bold)
            # else:
            #     # RESUMEN DE LOS TOTALES VENTAS
            #     # sheet.set_row(7,50 ) altura de las celdas
            #     sheet.merge_range('J8:M8', 'RESUMEN GENERAL', cell_format_2)
            #     sheet.write(7, 13, 'Base Imponible', cell_format_1)
            #     sheet.write(7, 14, 'Crédito  fiscal', cell_format_1)
            #     sheet.write(7, 15, 'IVA retenido por el comprador', cell_format_1)
            #     sheet.write(7, 16, 'IGTF pagado', cell_format_1)
            #
            #     sheet.merge_range('J9:M9', 'Total Compras Internas No Gravadas', title_style)
            #     sheet.merge_range('J10:M10', 'Total Compras de Exportación ', title_style)
            #     sheet.merge_range('J11:M11', 'Total Compras  Internas afectadas sólo alícuota general 16.00 ', title_style)
            #     sheet.merge_range('J12:M12', 'Total Compras Internas afectadas sólo alícuota reducida 8.00 ', title_style)
            #     sheet.merge_range('J13:M13', 'Total Compras Internas afectadas por alícuota general más adicional 26.00 ', title_style)
            #     sheet.merge_range('J14:M14', 'Total Notas de Crédito aplicadas en Compras ', title_style)
            #     sheet.merge_range('J15:M15', 'Total Notas de Débito  aplicadas en Compras ', title_style)
            #     sheet.merge_range('J16:M16', 'Total:', title_style)


