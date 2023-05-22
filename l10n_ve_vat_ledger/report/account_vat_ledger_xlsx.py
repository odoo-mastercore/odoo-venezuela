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
                sheet.write(4, 5, 'Número de Comprobante', cell_format)
                sheet.write(4, 6, 'Número Factura Afectada', cell_format)
                sheet.write(4, 7, 'Nª planilla de Importaciòn', cell_format)
                sheet.write(4, 8, 'Nª de Expediente de Importaciòn', cell_format)
                sheet.write(4, 9, 'Nombre o Razón Social', cell_format)
                sheet.write(4, 10, 'RIF', cell_format)
                sheet.write(4, 11, 'Total Compras  Bs. Incluyendo IVA.', cell_format)
                sheet.write(4, 12, 'Compras sin Derecho a Crédito I.V.A.', cell_format)

                # celda adicional compras por cuenta de terceros
                sheet.merge_range('N4:P4','Importaciones', cell_format)
                sheet.write(4, 13, 'Base Imponible', cell_format)
                sheet.write(4, 14, '% Alic.', cell_format)
                sheet.write(4, 15, 'Imp. I.V.A.', cell_format)

                # # IVA RETENIDO
                sheet.merge_range('Q4:V4', 'Compras Internas', cell_format)
                sheet.write(4, 16, 'Base Imponible', cell_format)
                sheet.write(4, 17, 'Alicuota 16% + Alicuota Adicional', cell_format)
                sheet.write(4, 18, 'Imp. I.V.A.', cell_format)
                sheet.write(4, 19, 'B. Imponible', cell_format)
                sheet.write(4, 20, 'Alicuota 8%', cell_format)
                sheet.write(4, 21, 'Imp. I.V.A.', cell_format)

                sheet.write(4, 22, 'I.V.A. Retenido por el comprador', cell_format)
                sheet.write(4, 23, 'I.G.T.F Pagado  ', cell_format)

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
                sheet.write(4, 5, 'N° comprobante', cell_format)
                sheet.write(4, 6, 'Número Factura Afectada', cell_format)
                sheet.write(4, 7, 'Nombre o Razón Social', cell_format)
                sheet.write(4, 8, 'RIF', cell_format)
                sheet.write(4, 9, 'Total Ventas  Bs. Incluyendo IVA.', cell_format)

                # celda adicional Ventas por cuenta de terceros
                sheet.merge_range('K4:N4', 'Ventas por cuenta de terceros', cell_format)
                sheet.write(4, 10, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 11, 'Base Imponible', cell_format)
                sheet.write(4, 12, '% Alicuota.', cell_format)
                sheet.write(4, 13, 'Impuesto I.V.A', cell_format)

                # celda adicional Contribuyente
                sheet.merge_range('O4:U4', 'Contribuyente', cell_format)
                sheet.write(4, 14, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 15, 'Base Imponible', cell_format)
                sheet.write(4, 16, '% Alicuota General + Adicional', cell_format)
                sheet.write(4, 17, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 18, 'Base Imponible', cell_format)
                sheet.write(4, 19, '% Alicuota Reducida', cell_format)
                sheet.write(4, 20, 'Impuesto I.V.A', cell_format)

                # celda adicional No Contribuyente
                sheet.merge_range('V4:AB4', 'No Contribuyente', cell_format)
                sheet.write(4, 21, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 22, 'Base Imponible', cell_format)
                sheet.write(4, 23, '% Alicuota.', cell_format)
                sheet.write(4, 24, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 25, 'Base Imponible', cell_format)
                sheet.write(4, 26, '% Alicuota Reducida', cell_format)
                sheet.write(4, 27, 'Impuesto I.V.A', cell_format)

                # celda adicional Retención IVA
                # sheet.merge_range('AB4:AD4', 'Retención IVA', cell_format)
                sheet.write(4, 28, 'I.V.A Retenido', cell_format)
                # sheet.write(4, 29, 'Factura afectada', cell_format)
                sheet.write(4, 29, 'I.G.T.F Percibido', cell_format)

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
            
            """ 
                Retenciones
             """
            tax_withholding_id = []
            retens = []
            if obj.type == 'purchase':
                tax_withholding_id = self.env['account.tax'].search([
                    ('type_tax_use', '=', 'purchase'),
                    ('withholding_type', '=', 'partner_tax')
                ], limit=1)
            else:
                tax_withholding_id = self.env['account.tax'].search([
                    ('type_tax_use', '=', 'customer'),
                    ('name', 'like', 'IVA')
                ], limit=1)
            if tax_withholding_id:
                retens = self.env['account.payment'].search([
                    ('tax_withholding_id', '=', tax_withholding_id.id),
                    ('state', '=', 'posted'),
                    ('date', '>=', obj.date_from),
                    ('date', '<=', obj.date_to),
                ])
            retenciones = []
            if retens:
                retenciones = list(retens)
            if obj.type == 'sale':
                invoices = reversed(obj.invoice_ids)
            elif obj.type == 'purchase':
                invoices = sorted(obj.invoice_ids, key=lambda x: x.invoice_date)
            
            date_reference = obj.date_from
            
            for idx, invoice in enumerate(invoices):
                if obj.type == 'purchase':
                    if date_reference <= invoice.invoice_date:
                        while date_reference < invoice.invoice_date:
                            coincident_date = [tup for tup in retenciones if date_reference == tup.date ]
                            if coincident_date:
                                for reten in coincident_date:
                                    total_iva_16_retenido += reten.amount
                                    i += 1
                                    # codigo 
                                    sheet.write(row, 0, i, line)
                                    # fehca
                                    sheet.write(row, 1, reten.date, date_line)
                                    # tipo de documento
                                    sheet.write(row, 2, 'Retención', line)
                                    sheet.write(row, 3, '', line)
                                    sheet.write(row, 4, '', line)
                                    # Numero de comrpobante
                                    sheet.write(row, 5, reten.withholding_number, line)
                                    # Documento afectado
                                    sheet.write(row, 6, reten.reconciled_bill_ids.ref, line)
                                    sheet.write(row, 7, '', line)
                                    sheet.write(row, 8, '', line)
                                    # Nombre
                                    sheet.write(row, 9, reten.move_id.partner_id.name, line)
                                    # RIF
                                    sheet.write(row, 10, '%s-%s' % (reten.move_id.partner_id. \
                                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                                        reten.move_id.partner_id.vat or 'FALSE'), line)
                                    #Total
                                    sheet.write(row, 11, '', line)
                                    # Compras Exento
                                    sheet.write(row, 12, '', line)

                                    #IMPORTACIONES
                                    # Base Imponible
                                    sheet.write(row, 13, '', line)
                                    # % Alic
                                    sheet.write(row, 14, '', line)
                                    #Imp. IVA
                                    sheet.write(row, 15, '', line)

                                    #Compras internas
                                    # Base Imponible
                                    sheet.write(row, 16, '', line)
                                    # % Alic
                                    sheet.write(row, 17, '', line)
                                    #Imp. IVA
                                    sheet.write(row, 18, '', line)

                                    #IVA 8%
                                    # Base Imponible
                                    sheet.write(row, 19, '', line)
                                    # % Alic
                                    sheet.write(row, 20, '', line)
                                    #Imp. IVA
                                    sheet.write(row, 21, '', line)
                                    

                                    #Retenciones
                                    sheet.write(row, 22, reten.amount, line)
                                    ###### IGTF
                                    sheet.write(row, 23, '', line)
                                    retenciones.remove(reten)
                                    row +=1
                            else:
                                date_reference += timedelta(days=1)

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
                    
                    
                    # Retencion
                    # Numero de comprobante
                    sheet.write(row, 5, '', line)

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
                            sheet.write(row, 6, inv_info, line)
                    else:
                        sheet.write(row, 6, '', line)

                    # Planilla de importacion
                    sheet.write(row, 7, '', line)
                    # Nro Expediente de importacion
                    sheet.write(row, 8, '', line)
                    # nombre del partner
                    sheet.write(row, 9, invoice.partner_id.name or 'FALSE', line)

                    # Rif del cliente
                    sheet.write(row, 10, '%s-%s' % (invoice.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        invoice.partner_id.vat or 'FALSE'), line)
                    # Tipo de Proveedor Compras
                    # sheet.write(row, 10, invoice.partner_id.l10n_ve_responsibility_type_id.name or 'FALSE', line)

                    #Total Compras con IVA
                    sheet.write(
                        row, 11, (invoice.amount_total_signed * -1.00), line)

                    ####IMPUESTOS##########
                    
                    base_exento = 0.00
                    base_imponible = 0.00
                    iva_16 = 0.00
                    alic_16 = ''
                    alic_8 = ''
                    iva_8 = 0.00
                    base_imponible_8 = 0.00
                    if invoice.line_ids:
                        for linel in invoice.line_ids:
                            if linel.tax_ids:
                                if linel.tax_ids[0].amount == 16.00:
                                    base_imponible += linel.debit if linel.credit == 0 else -linel.debit
                                    if invoice.move_type == 'out_refund' or \
                                        invoice.move_type == 'in_refund' or (invoice.move_type == 'out_invoice' \
                                            and invoice.debit_origin_id):
                                        base_imponible += (linel.credit * -1.00) if linel.credit == 0 else 0
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_16 += base_imponible
                                        else:
                                            base_imponible += linel.debit
                                            total_nota_debito_16 += base_imponible
                                    else:
                                        total_base_imponible_16 += base_imponible
                                    alic_16 = '16%'
                                elif linel.tax_ids[0].amount == 0.00:
                                    base_exento += linel.debit if linel.credit == 0 else -linel.debit
                                    if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                        or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        base_exento += linel.credit * -1.00 if linel.credit == 0 else 0
                                        if not invoice.debit_origin_id:
                                            total_base_exento_credito += base_exento
                                        else:
                                            base_exento += linel.debit
                                            total_base_exento_debito += base_exento
                                    else:
                                        total_base_exento += base_exento
                                elif linel.tax_ids[0].amount == 8.00:
                                    base_imponible_8 += linel.debit if linel.credit == 0 else -linel.debit
                                    if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                        or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        base_imponible_8 += linel.credit * -1.00 if linel.credit == 0 else 0
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_8 += base_imponible_8
                                        else:
                                            base_imponible_8 += linel.debit
                                            total_nota_debito_8 += base_imponible_8
                                    else:
                                        total_base_imponible_8 += base_imponible_8
                                    alic_8 = '8%'
                            elif linel.name == 'IVA (16.0%) compras':
                                iva_16 += linel.debit
                                if invoice.move_type == 'out_refund' or \
                                        invoice.move_type == 'in_refund' or (invoice.move_type == 'out_invoice' \
                                            and invoice.debit_origin_id):
                                    iva_16 += linel.credit * -1.00
                                    if not invoice.debit_origin_id:
                                        total_nota_credito_iva_16 += iva_16
                                    else:
                                        iva_16 += linel.debit
                                        total_nota_debito_iva_16 += iva_16
                                else:
                                    total_iva_16 += iva_16
                            elif linel.name == 'IVA (8.0%) compras':
                                iva_8 += linel.debit
                                if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                        or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                    iva_8 += linel.credit * -1.00
                                    if not invoice.debit_origin_id:
                                        total_nota_credito_iva_8 += iva_8
                                    else:
                                        iva_8 += linel.debit
                                        total_nota_debito_iva_8 += iva_8
                                else:
                                    total_iva_8 += iva_8
                                alic_8 = '8%'



                    #########
                    """ Totales """
                    c_total_base_exento += base_exento if base_exento else 0.00
                    c_total_base_imponible_16 += base_imponible if base_imponible else 0.00
                    c_total_iva_16 += iva_16 if iva_16 else 0.00
                    c_total_base_imponible_8 += base_imponible_8 if base_imponible_8 else 0.00
                    c_total_iva_8 += iva_8 if iva_8 else 0.00

                    # Compras Exento
                    sheet.write(row, 12, base_exento, line)

                    #IMPORTACIONES
                    # Base Imponible
                    sheet.write(row, 13, '', line)
                    # % Alic
                    sheet.write(row, 14, '', line)
                    #Imp. IVA
                    sheet.write(row, 15, '', line)

                    #Compras internas
                    # Base Imponible
                    sheet.write(row, 16, base_imponible, line)
                    # % Alic
                    sheet.write(row, 17, alic_16, line)
                    #Imp. IVA
                    sheet.write(row, 18, iva_16, line)

                    #IVA 8%
                    # Base Imponible
                    sheet.write(row, 19, base_imponible_8, line)
                    # % Alic
                    sheet.write(row, 20, alic_8, line)
                    #Imp. IVA
                    sheet.write(row, 21, iva_8, line)
                    

                    #Retenciones
                    sheet.write(row, 22, '', line)
                    ###### IGTF
                    sheet.write(row, 23, '', line)

                    
                elif obj.type == 'sale':
                    if date_reference <= invoice.invoice_date:
                        while date_reference < invoice.invoice_date:
                            coincident_date = [tup for tup in retenciones if date_reference == tup.date]
                            if coincident_date:
                                for reten in coincident_date:
                                    total_iva_16_retenido += reten.amount
                                    i += 1
                                    # contador de la factura
                                    sheet.write(row, 0, i, line)
                                    # codigo fecha
                                    sheet.write(row, 1, reten.date or 'FALSE', date_line)
                                    # tipo de documento
                                    sheet.write(row, 2, 'Retención', line)

                                    sheet.write(row, 3, '', line)
                                    sheet.write(row, 4, '', line)
                                    # Numero de comrpobante
                                    sheet.write(row, 5, reten.withholding_number, line)
                                    # Documento afectado
                                    if len(reten.reconciled_invoice_ids) > 1:
                                        sheet.write(row, 6, reten.reconciled_invoice_ids[0].name, line)
                                    else:
                                        sheet.write(row, 6, reten.reconciled_invoice_ids.name, line)
                                    # nombre del partner
                                    sheet.write(row, 7, reten.move_id.partner_id.name or 'FALSE', line)
                                    # Rif del cliente
                                    sheet.write(row, 8, '%s-%s' % (reten.move_id.partner_id. \
                                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                                        reten.move_id.partner_id.vat or 'FALSE'), line)
                                    sheet.write(row, 9, '', line)
                                    sheet.write(row, 10, '', line)
                                    sheet.write(row, 11, '', line)
                                    sheet.write(row, 12, '', line)
                                    sheet.write(row, 13, '', line)
                                    sheet.write(row, 14, '', line)
                                    sheet.write(row, 15, '', line)
                                    sheet.write(row, 16, '', line)
                                    sheet.write(row, 17, '', line)
                                    sheet.write(row, 18, '', line)
                                    sheet.write(row, 19, '', line)
                                    sheet.write(row, 20, '', line)
                                    sheet.write(row, 21, '', line)
                                    sheet.write(row, 22, '', line)
                                    sheet.write(row, 23, '', line)
                                    sheet.write(row, 24, '', line)
                                    sheet.write(row, 25, '', line)
                                    sheet.write(row, 26, '', line)
                                    sheet.write(row, 27, '', line)
                                    sheet.write(row, 28, reten.amount, line)
                                    sheet.write(row, 29, '', line)
                                    retenciones.remove(reten)
                                    row +=1
                            else:
                                date_reference += timedelta(days=1)
                                
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
                    sheet.write(row, 5, '', line)
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
                            sheet.write(row, 6, inv_origin.name, line)
                        else:
                            sheet.write(row, 6, '', line)
                    elif invoice.debit_origin_id:
                        sheet.write(row, 6, invoice.debit_origin_id.name, line)
                    else:
                        sheet.write(row, 6, '', line)
                    # nombre del partner
                    sheet.write(row, 7, invoice.partner_id.name or 'FALSE', line)
                    # Rif del cliente
                    sheet.write(row, 8, '%s-%s' % (invoice.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        invoice.partner_id.vat or 'FALSE'), line)

                    # Total Ventas Bs.Incluyendo IVA
                    if invoice.state != 'cancel':
                        sheet.write(row, 9, invoice.amount_total_signed, line)
                    else:
                        sheet.write(row, 9, '0', line)
                    
                    #Ventas por cuentas de tercero
                    sheet.write(row, 10, '', line)
                    sheet.write(row, 11, '', line)
                    sheet.write(row, 12, '', line)
                    sheet.write(row, 13, '', line)


                    # sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                    # Impuesto IVA Bs.
                    # sheet.write(row, 10, invoice.amount_tax_signed, line)
                    # if invoice.amount_tax_signed == 0:
                    #     sheet.write(row, 8, 'Exento', line)
                    # else:
                    #     sheet.write(row, 8, '16', line)

                    
                    #############################

                    ####IMPUESTOS##########
                    
                    base_exento = 0.00
                    base_imponible = 0.00
                    iva_16 = 0.00
                    alic_16 = ''
                    alic_8 = ''
                    iva_8 = 0.00
                    base_imponible_8 = 0.00
                    if invoice.line_ids:
                        for linel in invoice.line_ids:
                            if linel.tax_ids:
                                if linel.tax_ids[0].amount == 16.00:
                                    base_imponible += linel.credit if linel.debit == 0 else -linel.debit
                                    if invoice.move_type == 'out_refund' or \
                                        invoice.move_type == 'in_refund' or (invoice.move_type == 'out_invoice' \
                                            and invoice.debit_origin_id):
                                        base_imponible += (linel.debit * -1.00) if linel.debit == 0 else 0
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_16 += base_imponible
                                        else:
                                            base_imponible += linel.credit
                                            total_nota_debito_16 += base_imponible
                                    else:
                                        total_base_imponible_16 += base_imponible
                                    alic_16 = '16%'
                                elif linel.tax_ids[0].amount == 0.00:
                                    base_exento += linel.credit if linel.debit == 0 else -linel.debit
                                    if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                        or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        base_exento += linel.debit * -1.00 if linel.debit == 0 else 0
                                        if not invoice.debit_origin_id:
                                            total_base_exento_credito += base_exento
                                        else:
                                            base_exento += linel.credit
                                            total_base_exento_debito += base_exento
                                    else:
                                        total_base_exento += base_exento
                                elif linel.tax_ids[0].amount == 8.00:
                                    base_imponible_8 += linel.credit if linel.debit == 0 else -linel.debit
                                    if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                        or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        base_imponible_8 += linel.debit * -1.00 if linel.debit == 0 else 0
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_8 += base_imponible_8
                                        else:
                                            base_imponible_8 += linel.credit
                                            total_nota_debito_8 += base_imponible_8
                                    else:
                                        total_base_imponible_8 += base_imponible_8
                                    alic_8 = '8%'
                            elif linel.name == 'IVA (16.0%) ventas':
                                iva_16 += linel.credit
                                if invoice.move_type == 'out_refund' or \
                                        invoice.move_type == 'in_refund' or (invoice.move_type == 'out_invoice' \
                                            and invoice.debit_origin_id):
                                    iva_16 += linel.debit * -1.00
                                    if not invoice.debit_origin_id:
                                        total_nota_credito_iva_16 += iva_16
                                    else:
                                        iva_16 += linel.credit
                                        total_nota_debito_iva_16 += iva_16
                                else:
                                    total_iva_16 += iva_16
                            elif linel.name == 'IVA (8.0%) ventas':
                                iva_8 += linel.credit
                                if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                        or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                    iva_8 += linel.debit * -1.00
                                    if not invoice.debit_origin_id:
                                        total_nota_credito_iva_8 += iva_8
                                    else:
                                        iva_8 += linel.credit
                                        total_nota_debito_iva_8 += iva_8
                                else:
                                    total_iva_8 += iva_8
                                alic_8 = '8%'

                    #Contribuyentes
                    if invoice.partner_id.l10n_latam_identification_type_id.is_vat:
                        total_base_exento_contribuyente += base_exento if base_exento else 0.00
                        total_base_imponible_contribuyente_16 += base_imponible if base_imponible else 0.00
                        total_iva_contribuyente_16 += iva_16 if iva_16 else 0.00
                        total_base_imponible_contribuyente_8 += base_imponible_8 if base_imponible_8 else 0.00
                        total_iva_contribuyente_8 += iva_8 if iva_8 else 0.00

                        sheet.write(row, 14, base_exento, line)
                        sheet.write(row, 15, base_imponible, line)
                        sheet.write(row, 16, alic_16, line)
                        sheet.write(row, 17, iva_16, line)
                        sheet.write(row, 18, base_imponible_8, line)
                        sheet.write(row, 19, alic_8, line)
                        sheet.write(row, 20, iva_8, line)

                        sheet.write(row, 21, '', line)
                        sheet.write(row, 22, '', line)
                        sheet.write(row, 23, '', line)
                        sheet.write(row, 24, '', line)
                        sheet.write(row, 25, '', line)
                        sheet.write(row, 26, '', line)
                        sheet.write(row, 27, '', line)

                    #No contribuyentes
                    else:

                        total_base_exento_no_contribuyente += base_exento if base_exento else 0.00
                        total_base_imponible_no_contribuyente_16 += base_imponible if base_imponible else 0.00
                        total_iva_no_contribuyente_16 += iva_16 if iva_16 else 0.00
                        total_base_imponible_no_contribuyente_8 += base_imponible_8 if base_imponible_8 else 0.00
                        total_iva_no_contribuyente_8 += iva_8 if iva_8 else 0.00

                        sheet.write(row, 14, '', line)
                        sheet.write(row, 15, '', line)
                        sheet.write(row, 16, '', line)
                        sheet.write(row, 17, '', line)
                        sheet.write(row, 18, '', line)
                        sheet.write(row, 19, '', line)
                        sheet.write(row, 20, '', line)


                        sheet.write(row, 21, base_exento, line)
                        sheet.write(row, 22, base_imponible, line)
                        sheet.write(row, 23, alic_16, line)
                        sheet.write(row, 24, iva_16, line)
                        sheet.write(row, 25, base_imponible_8, line)
                        sheet.write(row, 26, alic_8, line)
                        sheet.write(row, 27, iva_8, line)
                        # sheet.write(row, 27, iva, line)
                   
                    
                #IGTF
                    sheet.write(row, 28, '', line)
                    sheet.write(row, 29, '', line)
                row += 1

            if len(retenciones) > 0 and obj.type == 'purchase':

                    # codigo 
                    sheet.write(row, 0, i, line)
                    # fehca
                    sheet.write(row, 1, reten.date, date_line)
                    # tipo de documento
                    sheet.write(row, 2, 'Retención', line)
                    sheet.write(row, 3, '', line)
                    sheet.write(row, 4, '', line)
                    # Numero de comrpobante
                    sheet.write(row, 5, reten.withholding_number, line)
                    # Documento afectado
                    sheet.write(row, 6, reten.reconciled_bill_ids.ref, line)
                    sheet.write(row, 7, '', line)
                    sheet.write(row, 8, '', line)
                    # Nombre
                    sheet.write(row, 9, reten.move_id.partner_id.name, line)
                    # RIF
                    sheet.write(row, 10, '%s-%s' % (reten.move_id.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        reten.move_id.partner_id.vat or 'FALSE'), line)
                    #Total
                    sheet.write(row, 11, '', line)
                    # Compras Exento
                    sheet.write(row, 12, '', line)

                    #IMPORTACIONES
                    # Base Imponible
                    sheet.write(row, 13, '', line)
                    # % Alic
                    sheet.write(row, 14, '', line)
                    #Imp. IVA
                    sheet.write(row, 15, '', line)

                    #Compras internas
                    # Base Imponible
                    sheet.write(row, 16, '', line)
                    # % Alic
                    sheet.write(row, 17, '', line)
                    #Imp. IVA
                    sheet.write(row, 18, '', line)

                    #IVA 8%
                    # Base Imponible
                    sheet.write(row, 19, '', line)
                    # % Alic
                    sheet.write(row, 20, '', line)
                    #Imp. IVA
                    sheet.write(row, 21, '', line)
                    

                    #Retenciones
                    sheet.write(row, 22, reten.amount, line)
                    ###### IGTF
                    sheet.write(row, 23, '', line)
                    retenciones.remove(reten)
                    row +=1

            elif len(retenciones) > 0 and obj.type == 'sale':
                for reten in sorted(retenciones, key=lambda x: x.date):
                    total_iva_16_retenido += reten.amount
                    i += 1
                    # contador de la factura
                    sheet.write(row, 0, i, line)
                    # codigo fecha
                    sheet.write(row, 1, reten.date or 'FALSE', date_line)
                    # tipo de documento
                    sheet.write(row, 2, 'Retención', line)

                    sheet.write(row, 3, '', line)
                    sheet.write(row, 4, '', line)
                    # Numero de comrpobante
                    sheet.write(row, 5, reten.withholding_number, line)
                    # Documento afectado
                    if len(reten.reconciled_invoice_ids) > 1:
                        sheet.write(row, 6, reten.reconciled_invoice_ids[0].name, line)
                    else:
                        sheet.write(row, 6, reten.reconciled_invoice_ids.name, line)
                    # nombre del partner
                    sheet.write(row, 7, reten.move_id.partner_id.name or 'FALSE', line)
                    # Rif del cliente
                    sheet.write(row, 8, '%s-%s' % (reten.move_id.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        reten.move_id.partner_id.vat or 'FALSE'), line)
                    sheet.write(row, 9, '', line)
                    sheet.write(row, 10, '', line)
                    sheet.write(row, 11, '', line)
                    sheet.write(row, 12, '', line)
                    sheet.write(row, 13, '', line)
                    sheet.write(row, 14, '', line)
                    sheet.write(row, 15, '', line)
                    sheet.write(row, 16, '', line)
                    sheet.write(row, 17, '', line)
                    sheet.write(row, 18, '', line)
                    sheet.write(row, 19, '', line)
                    sheet.write(row, 20, '', line)
                    sheet.write(row, 21, '', line)
                    sheet.write(row, 22, '', line)
                    sheet.write(row, 23, '', line)
                    sheet.write(row, 24, '', line)
                    sheet.write(row, 25, '', line)
                    sheet.write(row, 26, '', line)
                    sheet.write(row, 27, '', line)
                    sheet.write(row, 28, reten.amount, line)
                    sheet.write(row, 29, '', line)
                    retenciones.remove(reten)
                    row +=1

            if obj.type == 'sale':
                sheet.write((row), 14, total_base_exento_contribuyente, line_total)
                sheet.write((row), 15, total_base_imponible_contribuyente_16, line_total)
                sheet.write((row), 17, total_iva_contribuyente_16, line_total)
                sheet.write((row), 18, total_base_imponible_contribuyente_8, line_total)
                sheet.write((row), 20, total_iva_contribuyente_8, line_total)

                sheet.write((row), 21, total_base_exento_no_contribuyente, line_total)
                sheet.write((row), 22, total_base_imponible_no_contribuyente_16, line_total)
                sheet.write((row), 24, total_iva_no_contribuyente_16, line_total)
                sheet.write((row), 25, total_base_imponible_no_contribuyente_8, line_total)
                sheet.write((row), 27, total_iva_no_contribuyente_8, line_total)
                
                # RESUMEN DE LOS TOTALES VENTAS
                row +=5
                sheet.merge_range('J%s:M%s' % (str(row+1), str(row+1)), 'RESUMEN GENERAL', cell_format_2)
                sheet.write((row), 13, 'Base Imponible', cell_format_1)
                sheet.write((row), 14, 'Débito fiscal', cell_format_1)
                sheet.write((row), 15, 'IVA Retenido', cell_format_1)
                sheet.write((row), 16, 'IGTF percibido', cell_format_1)

                sheet.merge_range('J%s:M%s' % (str(row+2), str(row+2)),  'Total Ventas Internas No Gravadas', title_style)
                sheet.write((row+1), 13, round(total_base_exento_contribuyente + total_base_exento_no_contribuyente ,2), line)
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
                sheet.write((row+5), 13, round(total_base_imponible_contribuyente_16 + total_base_imponible_no_contribuyente_16,2), line)
                sheet.write((row+5), 14, total_iva_16, line)
                sheet.write((row+5), 15, total_iva_16_retenido, line)
                sheet.write((row+5), 16, total_iva_16_igtf, line)
                sheet.merge_range('J%s:M%s' % (str(row+7), str(row+7)), 'Total Ventas Internas afectadas sólo alícuota reducida 8.00', title_style)
                sheet.write((row+6), 13, round(total_base_imponible_contribuyente_8 + total_base_imponible_no_contribuyente_8,2), line)
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
                sheet.write((row+12), 13, round(total_base_exento_contribuyente + total_base_exento_no_contribuyente + total_base_imponible_contribuyente_16 \
                    + total_base_imponible_no_contribuyente_16 \
                        + total_base_imponible_contribuyente_8 + total_base_imponible_no_contribuyente_8 +total_nota_credito_16+\
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
                
                sheet.write((row), 12, c_total_base_exento, line_total)
                sheet.write((row), 16, c_total_base_imponible_16, line_total)
                sheet.write((row), 18, c_total_iva_16, line_total)
                sheet.write((row), 19, c_total_base_imponible_8, line_total)
                sheet.write((row), 21, c_total_iva_8, line_total)


                row += 5
                sheet.merge_range('J%s:M%s' % (str(row + 1), str(row + 1)), 'RESUMEN GENERAL', cell_format_2)
                sheet.write((row), 13, 'Base Imponible', cell_format_1)
                sheet.write((row), 14, 'Crédito  fiscal', cell_format_1)
                sheet.write((row), 15, 'IVA retenido por el comprador', cell_format_1)
                sheet.write((row), 16, 'IVA retenido a terceros', cell_format_1)

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