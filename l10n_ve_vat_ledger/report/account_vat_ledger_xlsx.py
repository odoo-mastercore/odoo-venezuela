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
            sheet = workbook.add_worksheet(report_name[:31])
            title = workbook.add_format({'bold': True})
            bold = workbook.add_format({'bold': True, 'border':1})


            # Resumen IVA
            # sheet2 = workbook.add_worksheet('Resumen consolidado de IVA')

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

            line_total = workbook.add_format({
                'border': 1,
                'fg_color': '#f0f0f0',
                'bold': 1,
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
            sheet.set_column(5, 30, 30)
# _____________________________________________________________________________________
# _____________________________________________________________________________________
            if obj.type == 'purchase':

                sheet.merge_range('A1:D1', obj.company_id.name,title_style)
                sheet.merge_range('A2:D2', _('%s-%s', obj.company_id.l10n_latam_identification_type_id.l10n_ve_code, obj.company_id.vat), title_style)
                sheet.merge_range('A3:G3', obj.name + ' ' + 'Libro de IVA Compras' + ' ' + 'mes' + ' ' + 'Año', title_style)

                # alto de las celdas
                sheet.set_row(4, 30)

                sheet.write(4, 0, 'Nro Oper.', cell_format)
                sheet.write(4, 1, 'Fecha de la Factura o Documento', cell_format)
                sheet.write(4, 2, 'Tipo de Documento', cell_format)
                sheet.write(4, 3, 'Número de Documento', cell_format)
                sheet.write(4, 4, 'Número de Control', cell_format)
                sheet.write(4, 5, 'Número Factura Afectada', cell_format)
                sheet.write(4, 6, 'Nª planilla de Importaciòn', cell_format)
                sheet.write(4, 7, 'Nª de Expediente de Importaciòn', cell_format)
                sheet.write(4, 8, 'Nombre o Razón Social', cell_format)
                sheet.write(4, 9, 'RIF', cell_format)
                sheet.write(4, 10, 'Total Compras  Bs. Incluyendo IVA.', cell_format)
                sheet.write(4, 11, 'Compras sin Derecho a Crédito I.V.A.', cell_format)

                # celda adicional compras por cuenta de terceros
                sheet.merge_range('M4:O4','Importaciones', cell_format)
                sheet.write(4, 12, 'Base Imponible', cell_format)
                sheet.write(4, 13, '% Alic.', cell_format)
                sheet.write(4, 14, 'Imp. I.V.A.', cell_format)

                # # IVA RETENIDO
                sheet.merge_range('P4:U4', 'Compras Internas', cell_format)
                sheet.write(4, 15, 'Base Imponible', cell_format)
                sheet.write(4, 16, 'Alicuota 16% + Alicuota Adicional', cell_format)
                sheet.write(4, 17, 'Imp. I.V.A.', cell_format)
                sheet.write(4, 18, 'B. Imponible', cell_format)
                sheet.write(4, 19, 'Alicuota 8%', cell_format)
                sheet.write(4, 20, 'Imp. I.V.A.', cell_format)

                sheet.write(4, 21, 'I.G.T.F Pagado  ', cell_format)
                sheet.write(4, 22, 'I.V.A. Retenido por el comprador', cell_format)

            elif obj.type == 'sale':

                sheet.merge_range('A1:D1', obj.company_id.name, title_style)
                # sheet.merge_range('E2:S2', 'LIBRO DE VENTAS (FECHA DESDE:' + ' ' + str(obj.date_from) + ' ' + 'HASTA:' + ' ' + str(obj.date_from) + ')', title)
                sheet.merge_range('A2:D2', _('%s-%s', obj.company_id.l10n_latam_identification_type_id.l10n_ve_code, obj.company_id.vat), title_style)
                sheet.merge_range('A3:G3', obj.name + ' ' + 'Libro de IVA Ventas' + ' ' + 'mes' + ' ' + 'Año',
                                  title_style)

                # alto de las celdas
                sheet.set_row(4, 30)

                sheet.write(4, 0, 'Nro Oper.', cell_format)
                sheet.write(4, 1, 'Fecha de la Factura', cell_format)
                sheet.write(4, 2, 'Tipo de Documento', cell_format)
                sheet.write(4, 3, 'Factura o Número de Documento', cell_format)
                sheet.write(4, 4, 'Número de Control', cell_format)
                sheet.write(4, 5, 'Número Factura Afectada', cell_format)
                sheet.write(4, 6, 'Nombre o Razón Social', cell_format)
                sheet.write(4, 7, 'RIF', cell_format)
                sheet.write(4, 8, 'Total Ventas  Bs. Incluyendo IVA.', cell_format)

                # celda adicional Ventas por cuenta de terceros
                sheet.merge_range('J4:M4', 'Ventas por cuenta de terceros', cell_format)
                sheet.write(4, 9, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 10, 'Base Imponible', cell_format)
                sheet.write(4, 11, '% Alicuota.', cell_format)
                sheet.write(4, 12, 'Impuesto I.V.A', cell_format)

                # celda adicional Contribuyente
                sheet.merge_range('N4:T4', 'Contribuyente', cell_format)
                sheet.write(4, 13, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 14, 'Base Imponible', cell_format)
                sheet.write(4, 15, '% Alicuota General + Adicional', cell_format)
                sheet.write(4, 16, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 17, 'Base Imponible', cell_format)
                sheet.write(4, 18, '% Alicuota Reducida', cell_format)
                sheet.write(4, 19, 'Impuesto I.V.A', cell_format)

                # celda adicional No Contribuyente
                sheet.merge_range('U4:AA4', 'No Contribuyente', cell_format)
                sheet.write(4, 20, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 21, 'Base Imponible', cell_format)
                sheet.write(4, 22, '% Alicuota.', cell_format)
                sheet.write(4, 23, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 24, 'Base Imponible', cell_format)
                sheet.write(4, 25, '% Alicuota Reducida', cell_format)
                sheet.write(4, 26, 'Impuesto I.V.A', cell_format)

                # celda adicional Retención IVA
                sheet.merge_range('AB4:AD4', 'Retención IVA', cell_format)
                sheet.write(4, 27, 'N° comprobante', cell_format)
                sheet.write(4, 28, 'I.V.A Retenido', cell_format)
                sheet.write(4, 29, 'Factura afectada', cell_format)
                sheet.write(4, 30, 'I.G.T.F Percibido', cell_format)

            row = 5
            total_base_exento = 0.00
            total_base_exento_credito = 0.00
            total_base_exento_debito = 0.00
            total_base_imponible_16 = 0.00
            total_iva_16 = 0.00
            total_iva_16_retenido = 0.00
            total_iva_16_igtf = 0.00

            total_base_imponible_8 = 0.00
            total_iva_8 = 0.00
            total_iva_8_igtf = 0.00

            total_base_imponible_15 = 0.00
            total_iva_15 = 0.00
            total_iva_15_igtf = 0.00
            alic = ''

            total_nota_credito_16 = 0.00
            total_nota_credito_iva_16 = 0.00
            total_nota_credito_8 = 0.00
            total_nota_credito_iva_8 = 0.00
            total_nota_debito_16 = 0.00
            total_nota_debito_iva_16 = 0.00
            total_nota_debito_8 = 0.00
            total_nota_debito_iva_8 = 0.00

            """ 
                Totales columnas ventas
             """

            total_base_exento_contribuyente = 0.00
            total_base_imponible_contribuyente_16 = 0.00
            total_iva_contribuyente_16 = 0.00
            total_base_imponible_contribuyente_8 = 0.00
            total_iva_contribuyente_8 = 0.00

            total_base_exento_no_contribuyente = 0.00
            total_base_imponible_no_contribuyente_16 = 0.00
            total_iva_no_contribuyente_16 = 0.00
            total_base_imponible_no_contribuyente_8 = 0.00
            total_iva_no_contribuyente_8 = 0.00

            """ 
                Totales columnas compras
             """

            c_total_base_exento = 0.00
            c_total_base_imponible_16 = 0.00
            c_total_iva_16 = 0.00
            c_total_base_imponible_8 = 0.00
            c_total_iva_8 = 0.00
          
            i = 0

            for invoice in reversed(obj.invoice_ids):
                if obj.type == 'purchase':
                    i += 1
                    # contador de la factura
                    sheet.write(row, 0, i, line)
                    # codigo fecha
                    sheet.write(row, 1, invoice.invoice_date or 'FALSE', date_line)
                    # tipo de documento
                    if invoice.move_type == 'out_invoice':
                        sheet.write(row, 2, 'Factura', line)
                    elif invoice.move_type == 'out_refund' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Credito', line)
                    elif invoice.move_type == 'out_refund' and invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Debito', line)
                    elif invoice.move_type == 'in_invoice':
                        sheet.write(row, 2, 'Factura', line)
                    elif invoice.move_type == 'in_refund' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Credito', line)
                    elif invoice.move_type == 'in_refund' and invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Debito', line)
                    # Número de Documento
                    sheet.write(row, 3, invoice.ref or '', line)
                    # Número de Control
                    sheet.write(row, 4, invoice.l10n_ve_document_number or '', line)

                    # Número Factura Afectada si es de debito o credito
                    if invoice.move_type == 'in_refund' or invoice.move_type == 'out_refund':
                        move_reconcileds = invoice._get_reconciled_info_JSON_values()
                        inv_info = ''
                        moves = []
                        if move_reconcileds:
                            for m in move_reconcileds:
                                moves.append(m['move_id'])
                            move_ids = self.env['account.move'].search(
                                [('id', 'in', moves)])
                            for mov in move_ids:
                                if mov.move_type == 'in_invoice' and mov.state == 'posted':
                                    inv_info = mov.ref
                            sheet.write(row, 5, inv_info, line)
                    else:
                        sheet.write(row, 5, '', line)

                    # Planilla de importacion
                    sheet.write(row, 6, '', line)
                    # Nro Expediente de importacion
                    sheet.write(row, 7, '', line)
                    # nombre del partner
                    sheet.write(row, 8, invoice.partner_id.name or 'FALSE', line)

                    # Rif del cliente
                    sheet.write(row, 9, '%s-%s' % (invoice.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        invoice.partner_id.vat or 'FALSE'), line)
                    # Tipo de Proveedor Compras
                    # sheet.write(row, 10, invoice.partner_id.l10n_ve_responsibility_type_id.name or 'FALSE', line)

                    #Total Compras con IVA
                    sheet.write(
                        row, 10, (invoice.amount_total_signed * -1.00), line)

                    ####IMPUESTOS##########
                    
                    if invoice.tax_totals_json:
                        jsdict = json.loads(invoice.tax_totals_json)
                        taxex = next(iter(jsdict['groups_by_subtotal']))
                        tax_total_dict = jsdict['groups_by_subtotal'][taxex]
                        taxes = sorted(
                            tax_total_dict, key=lambda x: x['tax_group_name'])
                        base_exento = 0.00
                        base_imponible = 0.00
                        iva_16 = 0.00
                        alic_16 = ''
                        alic_8 = ''
                        iva_8 = ''
                        base_imponible_8 = ''
                        for tax in taxes:
                            ###########EXENTOS###########
                            if tax['tax_group_name'] == 'IVA 0%':
                                if invoice.currency_id != invoice.company_id.currency_id:
                                    rate = invoice.invoice_rate(
                                        invoice.currency_id.id, invoice.date)
                                    base_exento = round(
                                        tax['tax_group_base_amount'] * (1/rate), 2)
                                else:
                                    base_exento = tax['tax_group_base_amount']
                                if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                    base_exento = base_exento * -1.00
                                    if invoice.debit_origin_id:
                                        base_exento = base_exento * -1.00
                                        total_base_exento_debito += base_exento
                                    else:
                                        total_base_exento_credito += base_exento
                                else:
                                    total_base_exento += base_exento
                            ###########16%###########
                            if tax['tax_group_name'] == 'IVA 16%':
                                if invoice.currency_id != invoice.company_id.currency_id:
                                    rate = invoice.invoice_rate(
                                            invoice.currency_id.id, invoice.date)
                                    base_imponible = round(
                                        tax['tax_group_base_amount'] * (1/rate), 2)
                                    iva_16 = base_imponible * 0.16
                                else:
                                    base_imponible = tax['tax_group_base_amount']
                                    iva_16 = tax['tax_group_amount']
                                if invoice.move_type == 'out_refund' \
                                        or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                    base_imponible = base_imponible * -1.00
                                    iva_16 = iva_16 * -1.00
                                    if not invoice.debit_origin_id:
                                        total_nota_credito_16 += base_imponible
                                        total_nota_credito_iva_16 += iva_16
                                    else:
                                        base_imponible = base_imponible * -1.00
                                        iva_16 = iva_16 * -1.00
                                        total_nota_debito_16 += base_imponible
                                        total_nota_debito_iva_16 += iva_16
                                else:
                                    total_iva_16 += iva_16
                                    total_base_imponible_16 += base_imponible
                                alic_16 = '16%'
                            ###########IVA 8%###########
                            if tax['tax_group_name'] == 'IVA 8%':
                                if invoice.currency_id != invoice.company_id.currency_id:
                                    rate = invoice.invoice_rate(
                                        invoice.currency_id.id, invoice.date)
                                    base_imponible_8 = round(
                                        tax['tax_group_base_amount'] * (1/rate), 2)
                                    iva_8 = base_imponible_8 * 0.08
                                else:
                                    base_imponible_8 = tax['tax_group_base_amount']
                                    iva_8 = tax['tax_group_amount']
                                if invoice.move_type == 'out_refund' \
                                        or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                    base_imponible_8 = base_imponible_8 * -1.00
                                    iva_8 = iva_8 * -1.00
                                    if not invoice.debit_origin_id:
                                        total_nota_credito_iva += iva_8
                                    else:
                                        base_imponible_8 = base_imponible_8 * -1.00
                                        iva_8 = iva_8 * -1.00
                                        total_nota_debito_8 = base_imponible_8
                                        total_nota_debito_iva_8 += iva_8
                                else:
                                    total_base_imponible_8 += base_imponible_8
                                    total_iva_8 += iva_8
                                alic_8 = '8%'
                            ########## IVA 15
                            if tax['tax_group_name'] == 'IVA 15%':
                                if invoice.currency_id != invoice.company_id.currency_id:
                                    rate = invoice.invoice_rate(
                                        invoice.currency_id.id, invoice.date)
                                    base_imponible_15 = round(
                                        tax['tax_group_base_amount'] * (1/rate), 2)
                                    iva_15 = base_imponible_15 * 0.15
                                    
                                else:
                                    base_imponible_15 = tax['tax_group_base_amount']
                                    iva_15 = tax['tax_group_amount']
                                if invoice.move_type == 'out_refund' \
                                        or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                    base_imponible_15 = base_imponible_15 * -1.00
                                    iva_15 = iva_15 * -1.00
                                    if not invoice.debit_origin_id:
                                        total_nota_credito_iva += iva_15
                                    else:
                                        total_nota_debito_iva += iva_15 * -1.00
                                else:
                                    total_base_imponible_15 += base_imponible_15
                                    total_iva_15 += iva_15
                                alic = '15%'


                    #########
                    """ Totales """
                    c_total_base_exento += base_exento if base_exento else 0.00
                    c_total_base_imponible_16 += base_imponible if base_imponible else 0.00
                    c_total_iva_16 += iva_16 if iva_16 else 0.00
                    c_total_base_imponible_8 += base_imponible_8 if base_imponible_8 else 0.00
                    c_total_iva_8 += iva_8 if iva_8 else 0.00

                    # Compras Exento
                    sheet.write(row, 11, base_exento, line)

                    #IMPORTACIONES
                    # Base Imponible
                    sheet.write(row, 12, '', line)
                    # % Alic
                    sheet.write(row, 13, '', line)
                    #Imp. IVA
                    sheet.write(row, 14, '', line)

                    #Compras internas
                    # Base Imponible
                    sheet.write(row, 15, base_imponible, line)
                    # % Alic
                    sheet.write(row, 16, alic_16, line)
                    #Imp. IVA
                    sheet.write(row, 17, iva_16, line)

                    #IVA 8%
                    # Base Imponible
                    sheet.write(row, 18, base_imponible_8, line)
                    # % Alic
                    sheet.write(row, 19, alic_8, line)
                    #Imp. IVA
                    sheet.write(row, 20, iva_8, line)
                    


                    ###### IGTF
                    sheet.write(row, 21, 0, line)

                    #Retenciones
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
                        reten = 0.00
                    total_iva_16_retenido += reten
                    ##### IVA RETENIDO
                    sheet.write(row, 22, reten, line)

                    # #### ANTICIPO IVA
                    # sheet.write(row, 23, '', line)


                elif obj.type == 'sale':
                    i += 1
                    # contador de la factura
                    sheet.write(row, 0, i, line)
                    # codigo fecha
                    sheet.write(row, 1, invoice.invoice_date or 'FALSE', date_line)
                    # tipo de documento
                    
                    if invoice.move_type == 'out_invoice' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Factura', line)
                    elif invoice.move_type == 'out_invoice' and invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Debito', line)
                    elif invoice.move_type == 'out_refund' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Credito', line)
                    elif invoice.move_type == 'in_invoice':
                        sheet.write(row, 2, 'Factura', line)
                    elif invoice.move_type == 'in_refund' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Credito', line)
                    elif invoice.move_type == 'in_refund' and invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Debito', line)

                    # Número de Documento
                    sheet.write(row, 3, invoice.name or 'FALSE', line)
                    # Número de Control
                    sheet.write(row, 4, invoice.l10n_ve_document_number or 'FALSE', line)
                    # Número Factura Afectada si es de debito o credito
                    if invoice.move_type == 'out_refund':
                        name_inv = invoice.ref[invoice.ref.find(': ')+2:] or ''
                        if len(name_inv) > 7:
                            name_inv = name_inv[:7]
                        inv_origin = ''
                        if name_inv:
                            inv_origin = self.env['account.move'].search([('name', '=', name_inv)], limit=1)
                        else:
                            sale_order_id = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])
                            for inv_sale_order in sale_order_id.invoice_ids:
                                if inv_sale_order.move_type == 'out_invoice' and inv_sale_order.state == 'posted':
                                    inv_origin = inv_sale_order

                        if inv_origin:
                            sheet.write(row, 5, inv_origin.name, line)
                        else:
                            sheet.write(row, 5, '', line)
                    elif invoice.debit_origin_id:
                        sheet.write(row, 5, invoice.debit_origin_id.name, line)
                    else:
                        sheet.write(row, 5, '', line)
                    # nombre del partner
                    sheet.write(row, 6, invoice.partner_id.name or 'FALSE', line)
                    # Rif del cliente
                    sheet.write(row, 7, '%s-%s' % (invoice.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        invoice.partner_id.vat or 'FALSE'), line)

                    # Total Ventas Bs.Incluyendo IVA
                    if invoice.state != 'cancel':
                        sheet.write(row, 8, invoice.amount_total_signed, line)
                    else:
                        sheet.write(row, 8, '0', line)
                    
                    #Ventas por cuentas de tercero
                    sheet.write(row, 9, '', line)
                    sheet.write(row, 10, '', line)
                    sheet.write(row, 11, '', line)
                    sheet.write(row, 12, '', line)


                    # sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                    # Impuesto IVA Bs.
                    # sheet.write(row, 10, invoice.amount_tax_signed, line)
                    # if invoice.amount_tax_signed == 0:
                    #     sheet.write(row, 8, 'Exento', line)
                    # else:
                    #     sheet.write(row, 8, '16', line)

                    
                    #############################

                    ####IMPUESTOS##########
                    
                    if invoice.tax_totals_json:
                        jsdict = json.loads(invoice.tax_totals_json)
                        taxex = next(iter(jsdict['groups_by_subtotal']))
                        tax_total_dict = jsdict['groups_by_subtotal'][taxex]
                        taxes = sorted(
                            tax_total_dict, key=lambda x: x['tax_group_name'])
                        base_exento = 0.00
                        base_imponible = 0.00
                        iva_16 = 0.00
                        alic_16 = ''
                        alic_8 = ''
                        iva_8 = ''
                        base_imponible_8 = ''
                        for tax in taxes:
                            ###########EXENTOS###########
                            if tax['tax_group_name'] == 'IVA 0%':
                                if invoice.state != 'cancel':
                                    if invoice.currency_id != invoice.company_id.currency_id:
                                        rate = invoice.invoice_rate(
                                            invoice.currency_id.id, invoice.invoice_date)
                                        base_exento = round(
                                            tax['tax_group_base_amount'] * (1/rate), 2)
                                    else:
                                        base_exento = tax['tax_group_base_amount']
                                    if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                        or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        base_exento = base_exento * -1.00
                                        if invoice.debit_origin_id:
                                            base_exento = base_exento * -1.00
                                            total_base_exento_debito += base_exento
                                        else:
                                            total_base_exento_credito += base_exento
                                    else:
                                        total_base_exento += base_exento
                            ###########16%###########
                            if tax['tax_group_name'] == 'IVA 16%':
                                if invoice.state != 'cancel':
                                    if invoice.currency_id != invoice.company_id.currency_id:
                                        rate = invoice.invoice_rate(
                                            invoice.currency_id.id, invoice.invoice_date)
                                        base_imponible = round(
                                            tax['tax_group_base_amount'] * (1/rate), 2)
                                        iva_16 = base_imponible * 0.16
                                    else:
                                        base_imponible = tax['tax_group_base_amount']
                                        iva_16 = tax['tax_group_amount']
                                    if invoice.move_type == 'out_refund' or \
                                        invoice.move_type == 'in_refund' or \
                                            (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        base_imponible = base_imponible * -1.00
                                        iva_16 = iva_16 * -1.00
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_16 += base_imponible
                                            total_nota_credito_iva_16 += iva_16
                                        else:
                                            base_imponible = base_imponible * -1.00
                                            iva_16 = iva_16 * -1.00
                                            total_nota_debito_16 += base_imponible
                                            total_nota_debito_iva_16 += iva_16
                                    else:
                                        total_base_imponible_16 += base_imponible
                                        total_iva_16 += iva_16
                                    alic_16 = '16%'
                            ###########IVA 8%###########
                            if tax['tax_group_name'] == 'IVA 8%':
                                if invoice.state != 'cancel':
                                    if invoice.currency_id != invoice.company_id.currency_id:
                                        rate = invoice.invoice_rate(
                                            invoice.currency_id.id, invoice.invoice_date)
                                        base_imponible_8 = round(
                                            tax['tax_group_base_amount'] * (1/rate), 2)
                                        iva_8 = base_imponible_8 * 0.08
                                    else:
                                        base_imponible_8 = tax['tax_group_base_amount']
                                        iva_8 = tax['tax_group_amount']

                                    if invoice.move_type == 'out_refund' \
                                        or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        base_imponible_8 = base_imponible_8 * -1.00
                                        iva_8 = iva_8 * -1.00
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_8 += base_imponible_8
                                            total_nota_credito_iva_8 += iva_8
                                        else:
                                            base_imponible_8 = base_imponible_8 * -1.00
                                            iva_8 = iva_8 * -1.00
                                            total_nota_debito_8 = base_imponible_8
                                            total_nota_debito_iva_8 += iva_8
                                    else:
                                        total_base_imponible_8 += base_imponible_8
                                        total_iva_8 += iva_8
                                    alic_8 = '8%'
                            ########## IVA 15
                            if tax['tax_group_name'] == 'IVA 15%':
                                if invoice.state != 'cancel':
                                    if invoice.currency_id != invoice.company_id.currency_id:
                                        rate = invoice.invoice_rate(
                                            invoice.currency_id.id, invoice.invoice_date)
                                        base_imponible_15 = round(
                                            tax['tax_group_base_amount'] * (1/rate), 2)
                                        iva_15 = base_imponible_15 * 0.15
                                        
                                    else:
                                        base_imponible_15 = tax['tax_group_base_amount']
                                        iva_15 = tax['tax_group_amount']
                                    if invoice.move_type == 'out_refund' or \
                                        invoice.move_type == 'in_refund' or \
                                            (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        base_imponible_15 = base_imponible_15 * -1.00
                                        iva_15 = iva_15 * -1.00
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_iva += iva_15
                                        else:
                                            total_nota_debito_iva += iva_15 * -1.00
                                    else:
                                        total_base_imponible_15 += base_imponible_15
                                        total_iva_15 += iva_15
                                    alic = '15%'

                    #########

                    #Contribuyentes
                    if invoice.partner_id.l10n_latam_identification_type_id.is_vat:
                        total_base_exento_contribuyente += base_exento if base_exento else 0.00
                        total_base_imponible_contribuyente_16 += base_imponible if base_imponible else 0.00
                        total_iva_contribuyente_16 += iva_16 if iva_16 else 0.00
                        total_base_imponible_contribuyente_8 += base_imponible_8 if base_imponible_8 else 0.00
                        total_iva_contribuyente_8 += iva_8 if iva_8 else 0.00

                        sheet.write(row, 13, base_exento, line)
                        sheet.write(row, 14, base_imponible, line)
                        sheet.write(row, 15, alic_16, line)
                        sheet.write(row, 16, iva_16, line)
                        sheet.write(row, 17, base_imponible_8, line)
                        sheet.write(row, 18, alic_8, line)
                        sheet.write(row, 19, iva_8, line)

                        sheet.write(row, 20, '', line)
                        sheet.write(row, 21, '', line)
                        sheet.write(row, 22, '', line)
                        sheet.write(row, 23, '', line)
                        sheet.write(row, 24, '', line)
                        sheet.write(row, 25, '', line)
                        sheet.write(row, 26, '', line)

                    #No contribuyentes
                    else:

                        total_base_exento_no_contribuyente += base_exento if base_exento else 0.00
                        total_base_imponible_no_contribuyente_16 += base_imponible if base_imponible else 0.00
                        total_iva_no_contribuyente_16 += iva_16 if iva_16 else 0.00
                        total_base_imponible_no_contribuyente_8 += base_imponible_8 if base_imponible_8 else 0.00
                        total_iva_no_contribuyente_8 += iva_8 if iva_8 else 0.00

                        sheet.write(row, 13, '', line)
                        sheet.write(row, 14, '', line)
                        sheet.write(row, 15, '', line)
                        sheet.write(row, 16, '', line)
                        sheet.write(row, 17, '', line)
                        sheet.write(row, 18, '', line)
                        sheet.write(row, 19, '', line)


                        sheet.write(row, 20, base_exento, line)
                        sheet.write(row, 21, base_imponible, line)
                        sheet.write(row, 22, alic_16, line)
                        sheet.write(row, 23, iva_16, line)
                        sheet.write(row, 24, base_imponible_8, line)
                        sheet.write(row, 25, alic_8, line)
                        sheet.write(row, 26, iva_8, line)
                        # sheet.write(row, 27, iva, line)

                    #Retenciones
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
                    total_iva_16_retenido += reten
                    
                    if reten > 0.00:
                        sheet.write(row, 27, res[0], line)
                        sheet.write(row, 28, reten, line)
                        sheet.write(row, 29, invoice.name, line)
                    else:
                        sheet.write(row, 27, '', line)
                        sheet.write(row, 28, '', line)
                        sheet.write(row, 29, '', line)
                    
                #IGTF
                    sheet.write(row, 30, '', line)
                row += 1

            if obj.type == 'sale':

                sheet.write((row), 13, total_base_exento_contribuyente, line_total)
                sheet.write((row), 14, total_base_imponible_contribuyente_16, line_total)
                sheet.write((row), 16, total_iva_contribuyente_16, line_total)
                sheet.write((row), 17, total_base_imponible_contribuyente_8, line_total)
                sheet.write((row), 19, total_iva_contribuyente_8, line_total)

                sheet.write((row), 20, total_base_exento_no_contribuyente, line_total)
                sheet.write((row), 21, total_base_imponible_no_contribuyente_16, line_total)
                sheet.write((row), 23, total_iva_no_contribuyente_16, line_total)
                sheet.write((row), 24, total_base_imponible_no_contribuyente_8, line_total)
                sheet.write((row), 26, total_iva_no_contribuyente_8, line_total)
                
                # RESUMEN DE LOS TOTALES VENTAS
                row +=5
                sheet.merge_range('J%s:M%s' % (str(row+1), str(row+1)), 'RESUMEN GENERAL', cell_format_2)
                sheet.write((row), 13, 'Base Imponible', cell_format_1)
                sheet.write((row), 14, 'Débito fiscal', cell_format_1)
                sheet.write((row), 15, 'IVA Retenido', cell_format_1)
                sheet.write((row), 16, 'IGTF percibido', cell_format_1)

                sheet.merge_range('J%s:M%s' % (str(row+2), str(row+2)),  'Total Ventas Internas No Gravadas', title_style)
                sheet.write((row+1), 13, round(total_base_exento,2), line)
                sheet.write((row+1), 14, '0', line)
                sheet.write((row+1), 15, '0', line)
                sheet.write((row+1), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+3), str(row+3)),  'Total Nota de Credito No Gravadas', title_style)
                sheet.write((row+2), 13, round(total_base_exento_credito,2), line)
                sheet.write((row+2), 14, '0', line)
                sheet.write((row+2), 15, '0', line)
                sheet.write((row+2), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+4), str(row+4)),  'Total Nota de Debito No Gravadas', title_style)
                sheet.write((row+3), 13, round(total_base_exento_debito,2), line)
                sheet.write((row+3), 14, '0', line)
                sheet.write((row+3), 15, '0', line)
                sheet.write((row+3), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+5), str(row+5)), 'Total Ventas de Exportación ', title_style)
                sheet.write((row+4), 13, '0', line)
                sheet.write((row+4), 14, '0', line)
                sheet.write((row+4), 15, '0', line)
                sheet.write((row+4), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+6), str(row+6)), 'Total Ventas Internas afectadas sólo alícuota general 16.00', title_style)
                sheet.write((row+5), 13, round(total_base_imponible_16,2), line)
                sheet.write((row+5), 14, total_iva_16, line)
                sheet.write((row+5), 15, total_iva_16_retenido, line)
                sheet.write((row+5), 16, total_iva_16_igtf, line)
                sheet.merge_range('J%s:M%s' % (str(row+7), str(row+7)), 'Total Ventas Internas afectadas sólo alícuota reducida 8.00', title_style)
                sheet.write((row+6), 13, total_base_imponible_8, line)
                sheet.write((row+6), 14, total_iva_8, line)
                sheet.write((row+6), 15, '0', line)
                sheet.write((row+6), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+8), str(row+8)), 'Total Ventas Internas afectadas  más adicional 31.00', title_style)
                sheet.write((row+7), 13, '0', line)
                sheet.write((row+7), 14, '0', line)
                sheet.write((row+7), 15, '0', line)
                sheet.write((row+7), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+9), str(row+9)), 'Total Notas de Crédito o Devoluciones aplicadas en Ventas 16%', title_style)
                sheet.write((row+8), 13, total_nota_credito_16, line)
                sheet.write((row+8), 14, total_nota_credito_iva_16, line)
                sheet.write((row+8), 15, '', line)
                sheet.write((row+8), 16, '', line)
                sheet.merge_range('J%s:M%s' % (str(row+10), str(row+10)), 'Total Notas de Crédito o Devoluciones aplicadas en Ventas 8%', title_style)
                sheet.write((row+9), 13, total_nota_credito_8, line)
                sheet.write((row+9), 14, total_nota_credito_iva_8, line)
                sheet.write((row+9), 15, '', line)
                sheet.write((row+9), 16, '', line)
                sheet.merge_range('J%s:M%s' % (str(row+11), str(row+11)), 'Total Notas de Débito o recargos aplicadas en Ventas 16%:', title_style)
                sheet.write((row+10), 13, total_nota_debito_16, line)
                sheet.write((row+10), 14, total_nota_debito_iva_16, line)
                sheet.write((row+10), 15, '', line)
                sheet.write((row+10), 16, '', line)
                sheet.merge_range('J%s:M%s' % (str(row+12), str(row+12)), 'Total Notas de Débito o recargos aplicadas en Ventas 8%:', title_style)
                sheet.write((row+11), 13, total_nota_debito_8, line)
                sheet.write((row+11), 14, total_nota_debito_iva_8, line)
                sheet.write((row+11), 15, '', line)
                sheet.write((row+11), 16, '', line)
                sheet.merge_range('J%s:M%s' % (str(row+13), str(row+13)), 'Total:', title_style)
                sheet.write((row+12), 13, round(total_base_exento + total_base_imponible_16 \
                    + total_base_imponible_8+total_nota_credito_16+\
                        + total_nota_credito_8 +total_nota_debito_16\
                            + total_nota_debito_8 + total_base_exento_credito \
                                + total_base_exento_debito,2), line)
                sheet.write((row+12), 14, (total_iva_16 + total_iva_8 + \
                    total_nota_credito_iva_16 + total_nota_credito_iva_8 + \
                        total_nota_debito_iva_16 + total_nota_debito_iva_8), line)
                sheet.write((row+12), 15, total_iva_16_retenido, line)
                sheet.write((row+12), 16, total_iva_16_igtf, line)

            # Totales de compras
            else:
                
                sheet.write((row), 11, c_total_base_exento, line_total)
                sheet.write((row), 15, c_total_base_imponible_16, line_total)
                sheet.write((row), 17, c_total_iva_16, line_total)
                sheet.write((row), 18, c_total_base_imponible_8, line_total)
                sheet.write((row), 20, c_total_iva_8, line_total)


                row += 5
                sheet.merge_range('J%s:M%s' % (str(row + 1), str(row + 1)), 'RESUMEN GENERAL', cell_format_2)
                sheet.write((row), 13, 'Base Imponible', cell_format_1)
                sheet.write((row), 14, 'Crédito  fiscal', cell_format_1)
                sheet.write((row), 15, 'IVA retenido por el comprador', cell_format_1)
                sheet.write((row), 16, 'IVA retenido por el comprador', cell_format_1)

                sheet.merge_range('J%s:M%s' % (str(row + 2), str(row + 2)), 'Total Compras Internas NO Gravadas',
                                  title_style)
                sheet.write((row + 1), 13, total_base_exento, line)
                sheet.write((row + 1), 14, '0', line)
                sheet.write((row + 1), 15, '0', line)
                sheet.write((row + 1), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row + 3), str(row + 3)), 'Total Notas de Credito NO Gravadas',
                                  title_style)
                sheet.write((row + 2), 13, total_base_exento_credito, line)
                sheet.write((row + 2), 14, '0', line)
                sheet.write((row + 2), 15, '0', line)
                sheet.write((row + 2), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row + 4), str(row + 4)), 'Total Notas de Debito NO Gravadas',
                                  title_style)
                sheet.write((row + 3), 13, total_base_exento_debito, line)
                sheet.write((row + 3), 14, '0', line)
                sheet.write((row + 3), 15, '0', line)
                sheet.write((row + 3), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row + 5), str(row + 5)), 'Total Compras de Importaciòn', title_style)
                sheet.write((row + 4), 13, '0', line)
                sheet.write((row + 4), 14, '0', line)
                sheet.write((row + 4), 15, '0', line)
                sheet.write((row + 4), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row + 6), str(row + 6)),
                                  'Total Compras Internas afectadas sólo alícuota general 16.00', title_style)
                sheet.write((row + 5), 13, round(total_base_imponible_16,2), line)
                sheet.write((row + 5), 14, total_iva_16, line)
                sheet.write((row + 5), 15, total_iva_16_retenido, line)
                sheet.write((row + 5), 16, total_iva_16_igtf, line)
                sheet.merge_range('J%s:M%s' % (str(row + 7), str(row + 7)),
                                  'Total Compras Internas afectadas sólo alícuota reducida 8.00', title_style)
                sheet.write((row + 6), 13, total_base_imponible_8, line)
                sheet.write((row + 6), 14, total_iva_8, line)
                sheet.write((row + 6), 15, '0', line)
                sheet.write((row + 6), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row + 8), str(row + 8)),
                                  'Total Compras Internas afectadas por alícuota general más adicional 31.00', title_style)
                sheet.write((row + 7), 13, '0', line)
                sheet.write((row + 7), 14, '0', line)
                sheet.write((row + 7), 15, '0', line)
                sheet.write((row + 7), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+9), str(row+9)), 'Total Notas de Crédito o Devoluciones aplicadas en Compras 16%', title_style)
                sheet.write((row+8), 13, total_nota_credito_16, line)
                sheet.write((row+8), 14, total_nota_credito_iva_16, line)
                sheet.write((row+8), 15, '', line)
                sheet.write((row+8), 16, '', line)
                sheet.merge_range('J%s:M%s' % (str(row+10), str(row+10)), 'Total Notas de Crédito o Devoluciones aplicadas en Compras 8%', title_style)
                sheet.write((row+9), 13, total_nota_credito_8, line)
                sheet.write((row+9), 14, total_nota_credito_iva_8, line)
                sheet.write((row+9), 15, '', line)
                sheet.write((row+9), 16, '', line)
                sheet.merge_range('J%s:M%s' % (str(row+11), str(row+11)), 'Total Notas de Débito o recargos aplicadas en Compras 16%:', title_style)
                sheet.write((row+10), 13, total_nota_debito_16, line)
                sheet.write((row+10), 14, total_nota_debito_iva_16, line)
                sheet.write((row+10), 15, '', line)
                sheet.write((row+10), 16, '', line)
                sheet.merge_range('J%s:M%s' % (str(row+12), str(row+12)), 'Total Notas de Débito o recargos aplicadas en Compras 8%:', title_style)
                sheet.write((row+11), 13, total_nota_debito_8, line)
                sheet.write((row+11), 14, total_nota_debito_iva_8, line)
                sheet.write((row+11), 15, '', line)
                sheet.write((row+11), 16, '', line)
                sheet.merge_range('J%s:M%s' % (str(row+13), str(row+13)), 'Total:', title_style)
                sheet.write((row+12), 13, round(total_base_exento + total_base_imponible_16 \
                    + total_base_imponible_8+total_nota_credito_16+\
                        + total_nota_credito_8 +total_nota_debito_16\
                            + total_nota_debito_8 + total_base_exento_credito +\
                                total_base_exento_debito ,2), line)
                sheet.write((row+12), 14, (total_iva_16 + total_iva_8 + \
                    total_nota_credito_iva_16 + total_nota_credito_iva_8 + \
                        total_nota_debito_iva_16 + total_nota_debito_iva_8), line)
                sheet.write((row+12), 15, total_iva_16_retenido, line)
                sheet.write((row+12), 16, total_iva_16_igtf, line)





