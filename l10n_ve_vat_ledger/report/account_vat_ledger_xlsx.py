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

    def get_amount_base_amount(self, line, tax=False):
        # Convertir usando la API de currency para evitar búsquedas N+1 en res.currency.rate
        base_imponible = 0
        tax_amount = 0
        total = 0
        company_currency = line.move_id.company_currency_id
        if line.currency_id != company_currency:
            try:
                base_imponible = line.currency_id._convert(
                    line.price_subtotal,
                    company_currency,
                    line.move_id.company_id,
                    line.move_id.l10n_ve_invoice_date,
                )
            except Exception:
                # Fallback: usar el subtotal sin conversión
                base_imponible = line.price_subtotal
        else:
            base_imponible = line.price_subtotal
        tax_amount = round((base_imponible * (tax / 100)), 2) if tax else 0
        total = tax_amount + base_imponible
        return {
            'base_imponible': round(base_imponible, 2),
            'tax_amount': tax_amount,
            'total': total,
        }

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

            line_number = workbook.add_format({
                'border': 1,
                'num_format': '#,##0.00',
                'align': 'center'})
            
            line_total = workbook.add_format({
                'border': 1,
                'fg_color': '#f0f0f0',
                'num_format': '#,##0.00',
                'bold': 1,
                'align': 'center'})

            date_line = workbook.add_format(
                {'border': 1, 'num_format': 'dd-mm-yyyy',
                 'align': 'center'})
            
            date_time_line = workbook.add_format(
                {'border': 1, 'num_format': 'dd-mm-yyyy hh:mm',
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
            sheet.set_column(5, 31, 31)
            sheet.set_column(5, 32, 32)
            sheet.set_column(5, 33, 33)
            sheet.set_column(5, 34, 34)
            sheet.set_column(5, 35, 35)
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
                sheet.merge_range('Q4:Z4', 'Compras Internas', cell_format)
                sheet.write(4, 16, 'Base Imponible', cell_format)
                sheet.write(4, 17, 'Alicuota 16%', cell_format)
                sheet.write(4, 18, 'Imp. I.V.A.', cell_format)
                sheet.write(4, 19, 'B. Imponible', cell_format)
                sheet.write(4, 20, 'Alicuota 8%', cell_format)
                sheet.write(4, 21, 'Imp. I.V.A.', cell_format)
                sheet.write(4, 22, 'B. Imponible', cell_format)
                sheet.write(4, 23, 'Alicuota 31%', cell_format)
                sheet.write(4, 24, 'Imp. I.V.A.', cell_format)

                sheet.write(4, 25, 'I.V.A. Retenido por el comprador', cell_format)
                sheet.write(4, 26, 'I.G.T.F Pagado  ', cell_format)

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
                sheet.merge_range('O4:X4', 'Contribuyente', cell_format)
                sheet.write(4, 14, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 15, 'Base Imponible', cell_format)
                sheet.write(4, 16, '% Alicuota General', cell_format)
                sheet.write(4, 17, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 18, 'Base Imponible', cell_format)
                sheet.write(4, 19, '% Alicuota Reducida', cell_format)
                sheet.write(4, 20, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 21, 'Base Imponible', cell_format)
                sheet.write(4, 22, '% Alicuota Adicional', cell_format)
                sheet.write(4, 23, 'Impuesto I.V.A', cell_format)

                # celda adicional No Contribuyente
                sheet.merge_range('Y4:AH4', 'No Contribuyente', cell_format)
                sheet.write(4, 24, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 25, 'Base Imponible', cell_format)
                sheet.write(4, 26, '% Alicuota.', cell_format)
                sheet.write(4, 27, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 28, 'Base Imponible', cell_format)
                sheet.write(4, 29, '% Alicuota Reducida', cell_format)
                sheet.write(4, 30, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 31, 'Base Imponible', cell_format)
                sheet.write(4, 32, '% Alicuota Adicional', cell_format)
                sheet.write(4, 33, 'Impuesto I.V.A', cell_format)

                # celda adicional Retención IVA
                sheet.write(4, 34, 'I.V.A Retenido', cell_format)
                sheet.write(4, 35, 'I.G.T.F Percibido', cell_format)

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

            total_base_imponible_31 = 0.00
            total_iva_31 = 0.00

            total_nota_credito_16 = 0.00
            total_nota_credito_iva_16 = 0.00
            total_nota_credito_8 = 0.00
            total_nota_credito_iva_8 = 0.00
            total_nota_credito_31 = 0.00
            total_nota_credito_iva_31 = 0.00
            total_nota_debito_16 = 0.00
            total_nota_debito_iva_16 = 0.00
            total_nota_debito_8 = 0.00
            total_nota_debito_iva_8 = 0.00
            total_nota_debito_31 = 0.00
            total_nota_debito_iva_31 = 0.00

            """ 
                Totales columnas ventas
             """

            total_base_exento_contribuyente = 0.00
            total_base_imponible_contribuyente_16 = 0.00
            total_iva_contribuyente_16 = 0.00
            total_base_imponible_contribuyente_8 = 0.00
            total_iva_contribuyente_8 = 0.00
            total_base_imponible_contribuyente_31 = 0.00
            total_iva_contribuyente_31 = 0.00

            total_base_exento_no_contribuyente = 0.00
            total_base_imponible_no_contribuyente_16 = 0.00
            total_iva_no_contribuyente_16 = 0.00
            total_base_imponible_no_contribuyente_8 = 0.00
            total_iva_no_contribuyente_8 = 0.00
            total_base_imponible_no_contribuyente_31 = 0.00
            total_iva_no_contribuyente_31 = 0.00
            total_igtf = 0.00

            """ 
                Totales columnas compras
             """

            c_total_base_exento = 0.00
            c_total_base_imponible_16 = 0.00
            c_total_iva_16 = 0.00
            c_total_base_imponible_8 = 0.00
            c_total_iva_8 = 0.00
            c_total_base_imponible_31 = 0.00
            c_total_iva_31 = 0.00
            c_total_igtf = 0.00
          
            i = 0
            
            """ 
                Retenciones
             """
            tax_withholding_id = []
            retens = obj.withholding_ids
            # Índice por fecha de retenciones (si no hay retenciones quedará vacío)
            retenciones_by_date = {}
            retenciones = []
            if retens:
                # Indexar retenciones por fecha para acceso O(1)
                for r in retens:
                    retenciones_by_date.setdefault(r.payment_id.date, []).append(r)
                retenciones = list(retens)
            if obj.type == 'sale':
                invoices = [inv for inv in obj.invoice_ids if inv.l10n_ve_invoice_date]
                invoices = sorted(invoices, key=lambda x: x.l10n_ve_invoice_date)
            elif obj.type == 'purchase':
                invoices = [inv for inv in obj.invoice_ids if inv.invoice_date]
                invoices = sorted(invoices, key=lambda x: x.invoice_date)
            
            date_reference = obj.date_from
            
            for idx, invoice in enumerate(invoices):
                if obj.type == 'purchase':
                    if date_reference <= invoice.invoice_date:
                        while date_reference < invoice.invoice_date:
                            coincident_date = retenciones_by_date.get(date_reference, [])
                            if coincident_date:
                                for reten in list(coincident_date):
                                    move_type_reten = reten.l10n_ve_move_line_taxes_ids[0].move_id.move_type
                                    amount_reten = reten.amount if move_type_reten == 'in_invoice' else reten.amount * -1.00
                                    total_iva_16_retenido += amount_reten
                                    i += 1
                                    # codigo 
                                    sheet.write(row, 0, i, line)
                                    # fehca
                                    sheet.write(row, 1, reten.payment_id.date, date_line)
                                    # tipo de documento
                                    sheet.write(row, 2, 'Retención', line)
                                    sheet.write(row, 3, '', line)
                                    sheet.write(row, 4, '', line)
                                    # Numero de comprobante
                                    sheet.write(row, 5, reten.name, line)
                                    # Documento afectado
                                    sheet.write(row, 6, reten.payment_id.invoice_ids.ref or '', line)
                                    sheet.write(row, 7, '', line)
                                    sheet.write(row, 8, '', line)
                                    # Nombre
                                    sheet.write(row, 9, reten.partner_id.name, line)
                                    # RIF
                                    sheet.write(row, 10, '%s-%s' % (reten.partner_id.l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                                        reten.partner_id.vat or 'FALSE'), line)
                                    #Total
                                    sheet.write(row, 11, '', line_number)
                                    # Compras Exento
                                    sheet.write(row, 12, '', line_number)

                                    #IMPORTACIONES
                                    # Base Imponible
                                    sheet.write(row, 13, '', line_number)
                                    # % Alic
                                    sheet.write(row, 14, '', line_number)
                                    #Imp. IVA
                                    sheet.write(row, 15, '', line_number)

                                    #Compras internas
                                    # Base Imponible
                                    sheet.write(row, 16, '', line_number)
                                    # % Alic
                                    sheet.write(row, 17, '', line_number)
                                    #Imp. IVA
                                    sheet.write(row, 18, '', line_number)

                                    #IVA 8%
                                    # Base Imponible
                                    sheet.write(row, 19, '', line_number)
                                    # % Alic
                                    sheet.write(row, 20, '', line_number)
                                    #Imp. IVA
                                    sheet.write(row, 21, '', line_number)

                                     #IVA 31%
                                    # Base Imponible
                                    sheet.write(row, 22, '', line_number)
                                    # % Alic
                                    sheet.write(row, 23, '', line_number)
                                    #Imp. IVA
                                    sheet.write(row, 24, '', line_number)
                                    

                                    #Retenciones
                                    sheet.write(row, 25, amount_reten, line_number)
                                    ###### IGTF
                                    sheet.write(row, 26, '', line_number)
                                    # eliminar de la lista y del índice
                                    try:
                                        retenciones.remove(reten)
                                    except ValueError:
                                        pass
                                    try:
                                        retenciones_by_date[reten.name].remove(reten)
                                        if not retenciones_by_date[reten.name]:
                                            del retenciones_by_date[reten.name]
                                    except Exception:
                                        pass
                                    row +=1
                            else:
                                date_reference += timedelta(days=1)

                    i += 1
                    # contador de la factura
                    sheet.write(row, 0, i, line)
                    # codigo fecha
                    sheet.write(row, 1, invoice.invoice_date or 'FALSE', date_time_line if obj.type == 'pruchase' else date_line)
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
                    sheet.write(row, 4, invoice.l10n_ve_control_number or '', line)

                    # Retencion
                    # Numero de comprobante
                    sheet.write(row, 5, '', line)

                    # Número Factura Afectada si es de debito o credito
                    if invoice.move_type == 'in_refund' or invoice.move_type == 'out_refund':
                        inv_info = invoice.reversed_entry_id
                        sheet.write(row, 6, inv_info.ref, line)
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
                        row, 11, (invoice.amount_total_signed * -1.00), line_number)

                    ####IMPUESTOS##########
                    
                    base_exento = 0.00
                    base_imponible = 0.00
                    iva_16 = 0.00
                    alic_16 = ''
                    alic_8 = ''
                    iva_8 = 0.00
                    alic_31 = ''
                    iva_31 = 0.00
                    base_imponible_8 = 0.00
                    base_imponible_31 = 0.00
                    igtf_amount = 0.00
                    if invoice.invoice_line_ids:
                        for linel in invoice.invoice_line_ids:
                            if linel.tax_ids:
                                tax_amount_value = linel.tax_ids[0].amount
                                if tax_amount_value in (16.00, 8.00, 31.00, 0.00):
                                    amounts = self.get_amount_base_amount(linel, tax_amount_value if tax_amount_value != 0.00 else False)
                                    base_val = amounts.get('base_imponible')
                                    tax_val = amounts.get('tax_amount')
                                    if base_val and tax_amount_value == 16.00:
                                        base_imponible += base_val
                                        iva_16 += tax_val
                                        if invoice.move_type in ('in_refund',) or (invoice.move_type == 'in_invoice' and invoice.debit_origin_id):
                                            base_imponible += base_val * -1
                                            iva_16 += tax_val * -1.00
                                            if not invoice.debit_origin_id:
                                                base_imponible += base_val * -1
                                                iva_16 += tax_val * -1.00
                                                total_nota_credito_16 += base_val * -1
                                                total_nota_credito_iva_16 += tax_val * -1
                                            else:
                                                base_imponible += base_val
                                                iva_16 += tax_val
                                                total_nota_debito_16 += base_val
                                                total_nota_debito_iva_16 += tax_val
                                        else:
                                            total_base_imponible_16 += base_imponible
                                            total_iva_16 += iva_16
                                        alic_16 = '16%'
                                    elif base_val and tax_amount_value == 0.00:
                                        base_exento += base_val
                                        if invoice.move_type in ('in_refund',) or (invoice.move_type == 'in_invoice' and invoice.debit_origin_id):
                                            base_exento += base_val * -1
                                            if not invoice.debit_origin_id:
                                                total_base_exento_credito += base_val * -1
                                            else:
                                                base_exento += base_val
                                                total_base_exento_debito += base_val
                                        else:
                                            total_base_exento += base_exento
                                    elif base_val and tax_amount_value == 8.00:
                                        base_imponible_8 += base_val
                                        iva_8 += tax_val
                                        if invoice.move_type in ('in_refund',) or (invoice.move_type == 'in_invoice' and invoice.debit_origin_id):
                                            base_imponible_8 += base_val * -1
                                            iva_8 += tax_val * -1.00
                                            if not invoice.debit_origin_id:
                                                base_imponible_8 += base_val * -1
                                                iva_8 += tax_val * -1.00
                                                total_nota_credito_8 += base_val * -1
                                                total_nota_credito_iva_8 += tax_val * -1
                                            else:
                                                base_imponible += base_val
                                                iva_16 += tax_val
                                                total_nota_debito_8 += base_val
                                                total_nota_debito_iva_8 += tax_val
                                        else:
                                            total_base_imponible_8 += base_imponible_8
                                            total_iva_8 += iva_8
                                        alic_8 = '8%'
                                    elif base_val and tax_amount_value == 31.00:
                                        base_imponible_31 += base_val
                                        iva_31 += tax_val
                                        if invoice.move_type in ('in_refund',) or (invoice.move_type == 'in_invoice' and invoice.debit_origin_id):
                                            base_imponible_31 += base_val * -1
                                            iva_31 += tax_val * -1.00
                                            if not invoice.debit_origin_id:
                                                base_imponible_31 += base_val * -1
                                                iva_31 += tax_val * -1.00
                                                total_nota_credito_31 += base_val * -1
                                                total_nota_credito_iva_31 += tax_val * -1
                                            else:
                                                base_imponible += base_val
                                                iva_16 += tax_val
                                                total_nota_debito_31 += base_val
                                                total_nota_debito_iva_31 += tax_val
                                        else:
                                            total_base_imponible_31 += base_imponible_31
                                            total_iva_31 += iva_31
                                        alic_31 = '31%'
                    # print(base_imponible)
                    # if invoice.igtf_purchase_apply_purchase:
                    #     igtf_amount = invoice.igtf_amount_purchase

                    #########
                    """ Totales """
                    c_total_base_exento += base_exento if base_exento else 0.00
                    c_total_base_imponible_16 += base_imponible if base_imponible else 0.00
                    c_total_iva_16 += iva_16 if iva_16 else 0.00
                    c_total_base_imponible_8 += base_imponible_8 if base_imponible_8 else 0.00
                    c_total_iva_8 += iva_8 if iva_8 else 0.00
                    c_total_base_imponible_31 += base_imponible_31 if base_imponible_31 else 0.00
                    c_total_iva_31 += iva_31 if iva_31 else 0.00
                    c_total_igtf += igtf_amount if igtf_amount else 0.00


                    # Compras Exento
                    sheet.write(row, 12, base_exento, line_number)

                    #IMPORTACIONES
                    # Base Imponible
                    sheet.write(row, 13, 0, line_number)
                    # % Alic
                    sheet.write(row, 14, '', line_number)
                    #Imp. IVA
                    sheet.write(row, 15, 0, line_number)

                    #Compras internas
                    # Base Imponible
                    sheet.write(row, 16, base_imponible, line_number)
                    # % Alic
                    sheet.write(row, 17, alic_16, line_number)
                    #Imp. IVA
                    sheet.write(row, 18, iva_16, line_number)

                    #IVA 8%
                    # Base Imponible
                    sheet.write(row, 19, base_imponible_8, line_number)
                    # % Alic
                    sheet.write(row, 20, alic_8, line_number)
                    #Imp. IVA
                    sheet.write(row, 21, iva_8, line_number)

                    #IVA 31%
                    # Base Imponible
                    sheet.write(row, 22, base_imponible_31, line_number)
                    # % Alic
                    sheet.write(row, 23, alic_31, line_number)
                    #Imp. IVA
                    sheet.write(row, 24, iva_31, line_number)
                    

                    #Retenciones
                    sheet.write(row, 25, 0, line_number)
                    ###### IGTF
                    sheet.write(row, 26, igtf_amount, line_number)

                    
                elif obj.type == 'sale':
                    # Asegurar que comparamos fechas con fechas (invoice puede tener datetime)
                    inv_date = invoice.l10n_ve_invoice_date
                    if isinstance(inv_date, datetime):
                        inv_date = inv_date.date()
                    if not inv_date:
                        continue  # Salta facturas sin fecha válida
                    if date_reference <= inv_date:
                        while date_reference < inv_date:
                            # usar índice por fecha cuando esté disponible
                            coincident_date = retenciones_by_date.get(date_reference, []) if 'retenciones_by_date' in locals() else [tup for tup in retenciones if date_reference == tup.date]
                            if coincident_date:
                                for reten in coincident_date:
                                    total_iva_16_retenido += reten.amount if reten.currency_id.id == reten.company_id.currency_id.id else reten.amount_company_currency
                                    i += 1
                                    # contador de la factura
                                    sheet.write(row, 0, i, line)
                                    # codigo fecha
                                    sheet.write(row, 1, reten.payment_id.date or 'FALSE', date_line)
                                    # tipo de documento
                                    sheet.write(row, 2, 'Retención', line)

                                    sheet.write(row, 3, '', line)
                                    sheet.write(row, 4, '', line)
                                    # Numero de comrpobante
                                    sheet.write(row, 5, reten.name, line)
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
                                    sheet.write(row, 34, reten.amount if reten.currency_id.id == reten.company_id.currency_id.id else reten.amount_company_currency, line)
                                    sheet.write(row, 35, '', line)
                                    retenciones.remove(reten)
                                    row +=1
                            else:
                                date_reference += timedelta(days=1)
                    
                    i += 1

                    # contador de la factura
                    sheet.write(row, 0, i, line)
                    # codigo fecha
                    sheet.write(row, 1, invoice.l10n_ve_invoice_date or 'FALSE', date_time_line)
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
                    sheet.write(row, 4, invoice.l10n_ve_control_number or 'FALSE', line)

                    # Factura cancelada
                    if invoice.state == 'cancel':
                        sheet.write(row, 5, '', line)
                        sheet.write(row, 6, '', line)
                        sheet.write(row, 7, 'ANULADA', line)

                    
                    else:
                        sheet.write(row, 5, '', line)
                        # Número Factura Afectada si es de debito o credito
                        if invoice.move_type == 'out_refund':
                            if invoice.reversed_entry_id:
                                sheet.write(row, 6, invoice.reversed_entry_id.name, line)
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
                            sheet.write(row, 9, invoice.amount_total_signed, line_number)
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
                        alic_31 = ''
                        iva_31 = 0.00
                        base_imponible_31 = 0.00
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
                                                total_nota_credito_16 += linel.debit * -1.00
                                            else:
                                                # base_imponible += linel.credit
                                                total_nota_debito_16 += linel.credit
                                        else:
                                            total_base_imponible_16 += linel.credit if linel.debit == 0 else -linel.debit
                                        alic_16 = '16%'
                                    elif linel.tax_ids[0].amount == 0.00:
                                        base_exento += linel.credit if linel.debit == 0 else -linel.debit
                                        if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                            base_exento += linel.debit * -1.00 if linel.debit == 0 else 0
                                            if not invoice.debit_origin_id:
                                                total_base_exento_credito += linel.debit * -1.00
                                            else:
                                                # base_exento += linel.credit
                                                total_base_exento_debito += linel.credit
                                        else:
                                            total_base_exento += linel.credit if linel.debit == 0 else -linel.debit
                                    elif linel.tax_ids[0].amount == 8.00:
                                        base_imponible_8 += linel.credit if linel.debit == 0 else -linel.debit
                                        if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                            base_imponible_8 += linel.debit * -1.00 if linel.debit == 0 else 0
                                            if not invoice.debit_origin_id:
                                                total_nota_credito_8 += linel.debit * -1.00
                                            else:
                                                # base_imponible_8 += linel.credit
                                                total_nota_debito_8 += linel.credit
                                        else:
                                            total_base_imponible_8 += linel.credit if linel.debit == 0 else -linel.debit
                                        alic_8 = '8%'
                                    elif linel.tax_ids[0].amount == 31.00:
                                        base_imponible_31 += linel.credit if linel.debit == 0 else -linel.debit
                                        if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                            base_imponible_31 += linel.debit * -1.00 if linel.debit == 0 else 0
                                            if not invoice.debit_origin_id:
                                                total_nota_credito_31 += linel.debit * -1.00
                                            else:
                                                # base_imponible_31 += linel.credit
                                                total_nota_debito_31 += linel.credit
                                        else:
                                            total_base_imponible_31 += linel.credit if linel.debit == 0 else -linel.debit
                                        alic_31 = '31%'
                                elif linel.name == 'IVA (16.0%) ventas':
                                    iva_16 += linel.credit
                                    if invoice.move_type == 'out_refund' or \
                                            invoice.move_type == 'in_refund' or (invoice.move_type == 'out_invoice' \
                                                and invoice.debit_origin_id):
                                        iva_16 += linel.debit * -1.00
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_iva_16 += iva_16
                                        else:
                                            # iva_16 += linel.credit
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
                                            # iva_8 += linel.credit
                                            total_nota_debito_iva_8 += iva_8
                                    else:
                                        total_iva_8 += iva_8
                                    alic_8 = '8%'
                                elif linel.name == 'IVA (31.0%) ventas':
                                    iva_31 += linel.credit
                                    if invoice.move_type == 'out_refund' or invoice.move_type == 'in_refund' \
                                            or (invoice.move_type == 'out_invoice' and invoice.debit_origin_id):
                                        iva_31 += linel.debit * -1.00
                                        if not invoice.debit_origin_id:
                                            total_nota_credito_iva_31 += iva_31
                                        else:
                                            # iva_8 += linel.credit
                                            total_nota_debito_iva_31 += iva_31
                                    else:
                                        total_iva_31 += iva_31
                                    alic_31 = '31%'
                        
                        #Contribuyentes
                        if invoice.partner_id.l10n_latam_identification_type_id.is_vat:
                            total_base_exento_contribuyente += base_exento if base_exento else 0.00
                            total_base_imponible_contribuyente_16 += base_imponible if base_imponible else 0.00
                            total_iva_contribuyente_16 += iva_16 if iva_16 else 0.00
                            total_base_imponible_contribuyente_8 += base_imponible_8 if base_imponible_8 else 0.00
                            total_iva_contribuyente_8 += iva_8 if iva_8 else 0.00
                            total_base_imponible_contribuyente_31 += base_imponible_31 if base_imponible_31 else 0.00
                            total_iva_contribuyente_31 += iva_31 if iva_31 else 0.00

                            sheet.write(row, 14, base_exento, line_number)
                            sheet.write(row, 15, base_imponible, line_number)
                            sheet.write(row, 16, alic_16, line_number)
                            sheet.write(row, 17, iva_16, line_number)
                            sheet.write(row, 18, base_imponible_8, line_number)
                            sheet.write(row, 19, alic_8, line_number)
                            sheet.write(row, 20, iva_8, line_number)
                            sheet.write(row, 21, base_imponible_31, line_number)
                            sheet.write(row, 22, alic_31, line_number)
                            sheet.write(row, 23, iva_31, line_number)

                            sheet.write(row, 24, '', line)
                            sheet.write(row, 25, '', line)
                            sheet.write(row, 26, '', line)
                            sheet.write(row, 27, '', line)
                            sheet.write(row, 28, '', line)
                            sheet.write(row, 29, '', line)
                            sheet.write(row, 30, '', line)
                            sheet.write(row, 31, '', line)
                            sheet.write(row, 32, '', line)
                            sheet.write(row, 33, '', line)

                        #No contribuyentes
                        else:

                            total_base_exento_no_contribuyente += base_exento if base_exento else 0.00
                            total_base_imponible_no_contribuyente_16 += base_imponible if base_imponible else 0.00
                            total_iva_no_contribuyente_16 += iva_16 if iva_16 else 0.00
                            total_base_imponible_no_contribuyente_8 += base_imponible_8 if base_imponible_8 else 0.00
                            total_iva_no_contribuyente_8 += iva_8 if iva_8 else 0.00
                            total_base_imponible_no_contribuyente_31 += base_imponible_31 if base_imponible_31 else 0.00
                            total_iva_no_contribuyente_31 += iva_31 if iva_31 else 0.00

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


                            sheet.write(row, 24, base_exento, line_number)
                            sheet.write(row, 25, base_imponible, line_number)
                            sheet.write(row, 26, alic_16, line_number)
                            sheet.write(row, 27, iva_16, line_number)
                            sheet.write(row, 28, base_imponible_8, line_number)
                            sheet.write(row, 29, alic_8, line_number)
                            sheet.write(row, 30, iva_8, line_number)
                            sheet.write(row, 31, base_imponible_31, line_number)
                            sheet.write(row, 32, alic_31, line_number)
                            sheet.write(row, 33, iva_31, line_number)
                            # sheet.write(row, 27, iva, line)
                    
                        
                         #IGTF
            
                        igtf_amount = 0
                        # if invoice.payment_group_ids:
                        #     payments = invoice.payment_group_ids.mapped('payment_ids')
                        #     if payments and 'is_igtf' in self.env['account.payment']._fields:
                        #         payments_with_igtf = payments.filtered(lambda x: x.is_igtf)
                        #         for pay in payments_with_igtf:
                        #             igtf_amount += pay.igtf_amount_signed
                        total_igtf += igtf_amount
                        sheet.write(row, 34, '', line_number)
                        sheet.write(row, 35, igtf_amount if igtf_amount > 0 else '' , line_number)
                row += 1

            if obj.type == 'purchase':
                for reten in retenciones:
                    move_type_reten = reten.l10n_ve_move_line_taxes_ids[0].move_id.move_type
                    amount_reten = reten.amount if move_type_reten == 'in_invoice' else reten.amount * -1.00
                    total_iva_16_retenido += amount_reten
                    i += 1
                    # codigo 
                    sheet.write(row, 0, i, line)
                    # fecha
                    sheet.write(row, 1, reten.payment_id.date, date_line)
                    # tipo de documento
                    sheet.write(row, 2, 'Retención', line)
                    sheet.write(row, 3, '', line)
                    sheet.write(row, 4, '', line)
                    # Numero de comrpobante
                    sheet.write(row, 5, reten.name, line)
                    # Documento afectado
                    sheet.write(row, 6, reten.payment_id.invoice_ids.ref or '', line)
                    sheet.write(row, 7, '', line)
                    sheet.write(row, 8, '', line)
                    # Nombre
                    sheet.write(row, 9, reten.partner_id.name, line)
                    # RIF
                    sheet.write(row, 10, '%s-%s' % (reten.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        reten.partner_id.vat or 'FALSE'), line)
                    #Total
                    sheet.write(row, 11, '', line_number)
                    # Compras Exento
                    sheet.write(row, 12, '', line_number)

                    #IMPORTACIONES
                    # Base Imponible
                    sheet.write(row, 13, '', line_number)
                    # % Alic
                    sheet.write(row, 14, '', line_number)
                    #Imp. IVA
                    sheet.write(row, 15, '', line_number)

                    #Compras internas
                    # Base Imponible
                    sheet.write(row, 16, '', line_number)
                    # % Alic
                    sheet.write(row, 17, '', line_number)
                    #Imp. IVA
                    sheet.write(row, 18, '', line_number)

                    #IVA 8%
                    # Base Imponible
                    sheet.write(row, 19, '', line_number)
                    # % Alic
                    sheet.write(row, 20, '', line_number)
                    #Imp. IVA
                    sheet.write(row, 21, '', line_number)

                        #IVA 31%
                    # Base Imponible
                    sheet.write(row, 22, '', line_number)
                    # % Alic
                    sheet.write(row, 23, '', line_number)
                    #Imp. IVA
                    sheet.write(row, 24, '', line_number)
                    
                    #Retenciones
                    sheet.write(row, 25, amount_reten, line_number)
                    ###### IGTF
                    sheet.write(row, 26, '', line_number)
                    # No eliminar elementos de la lista mientras se itera
                    row +=1

            elif len(retenciones) >= 1 and obj.type == 'sale':
                for reten in sorted(retenciones, key=lambda x: x.payment_id.date):
                    total_iva_16_retenido += reten.amount if reten.currency_id.id == reten.company_id.currency_id.id else reten.amount_company_currency
                    i += 1
                    # contador de la factura
                    sheet.write(row, 0, i, line)
                    # codigo fecha
                    sheet.write(row, 1, reten.payment_id.date or 'FALSE', date_line)
                    # tipo de documento
                    sheet.write(row, 2, 'Retención', line)

                    sheet.write(row, 3, '', line)
                    sheet.write(row, 4, '', line)
                    # Numero de comrpobante
                    sheet.write(row, 5, reten.name, line)
                    # Documento afectado
                    sheet.write(row, 6, reten.payment_id.invoice_ids.name, line)
                    # nombre del partner
                    sheet.write(row, 7, reten.payment_id.partner_id.name or 'FALSE', line)
                    # Rif del cliente
                    sheet.write(row, 8, '%s-%s' % (reten.payment_id.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        reten.payment_id.partner_id.vat or 'FALSE'), line)
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
                    sheet.write(row, 28, '', line)
                    sheet.write(row, 29, '', line)
                    sheet.write(row, 30, '', line)
                    sheet.write(row, 31, '', line)
                    sheet.write(row, 32, '', line)
                    sheet.write(row, 33, '', line)
                    sheet.write(row, 34, reten.amount, line_number)
                    sheet.write(row, 35, '', line)
                    retenciones.remove(reten)
                    row +=1

            if obj.type == 'sale':
                sheet.write((row), 14, total_base_exento_contribuyente, line_total)
                sheet.write((row), 15, total_base_imponible_contribuyente_16, line_total)
                sheet.write((row), 17, total_iva_contribuyente_16, line_total)
                sheet.write((row), 18, total_base_imponible_contribuyente_8, line_total)
                sheet.write((row), 20, total_iva_contribuyente_8, line_total)
                sheet.write((row), 21, total_base_imponible_contribuyente_31, line_total)
                sheet.write((row), 23, total_iva_contribuyente_31, line_total)

                sheet.write((row), 24, total_base_exento_no_contribuyente, line_total)
                sheet.write((row), 26, total_base_imponible_no_contribuyente_16, line_total)
                sheet.write((row), 27, total_iva_no_contribuyente_16, line_total)
                sheet.write((row), 29, total_base_imponible_no_contribuyente_8, line_total)
                sheet.write((row), 30, total_iva_no_contribuyente_8, line_total)
                sheet.write((row), 31, total_base_imponible_no_contribuyente_31, line_total)
                sheet.write((row), 33, total_iva_no_contribuyente_31, line_total)
                sheet.write((row), 35, total_igtf, line_total)
                
                # RESUMEN DE LOS TOTALES VENTAS
                row +=5
                sheet.merge_range('J%s:M%s' % (str(row+1), str(row+1)), 'RESUMEN GENERAL', cell_format_2)
                sheet.write((row), 13, 'Base Imponible', cell_format_1)
                sheet.write((row), 14, 'Débito fiscal', cell_format_1)
                sheet.write((row), 15, 'IVA Retenido', cell_format_1)
                sheet.write((row), 16, 'IGTF percibido', cell_format_1)

                sheet.merge_range('J%s:M%s' % (str(row+2), str(row+2)),  'Total Ventas Internas No Gravadas', title_style)
                sheet.write((row+1), 13, round(total_base_exento_contribuyente + total_base_exento_no_contribuyente ,2), line_number)
                sheet.write((row+1), 14, 0, line_number)
                sheet.write((row+1), 15, 0, line_number)
                sheet.write((row+1), 16, '', line_number)
                sheet.merge_range('J%s:M%s' % (str(row+3), str(row+3)),  'Total Nota de Credito No Gravadas', title_style)
                sheet.write((row+2), 13, round(total_base_exento_credito,2), line_number)
                sheet.write((row+2), 14, 0, line_number)
                sheet.write((row+2), 15, 0, line_number)
                sheet.write((row+2), 16, '', line_number)
                sheet.merge_range('J%s:M%s' % (str(row+4), str(row+4)),  'Total Nota de Debito No Gravadas', title_style)
                sheet.write((row+3), 13, round(total_base_exento_debito,2), line_number)
                sheet.write((row+3), 14, 0, line_number)
                sheet.write((row+3), 15, 0, line_number)
                sheet.write((row+3), 16, '', line_number)
                sheet.merge_range('J%s:M%s' % (str(row+5), str(row+5)), 'Total Ventas de Exportación ', title_style)
                sheet.write((row+4), 13, 0, line_number)
                sheet.write((row+4), 14, 0, line_number)
                sheet.write((row+4), 15, 0, line_number)
                sheet.write((row+4), 16, '', line_number)
                sheet.merge_range('J%s:M%s' % (str(row+6), str(row+6)), 'Total Ventas Internas afectadas sólo alícuota general 16.00', title_style)
                sheet.write((row+5), 13, round(total_base_imponible_contribuyente_16 + total_base_imponible_no_contribuyente_16 - total_nota_credito_16 - total_nota_debito_16,2), line_number)
                sheet.write((row+5), 14, total_iva_16, line_number)
                sheet.write((row+5), 15, total_iva_16_retenido, line_number)
                sheet.write((row+5), 16, '', line_number)
                sheet.merge_range('J%s:M%s' % (str(row+7), str(row+7)), 'Total Ventas Internas afectadas sólo alícuota reducida 8.00', title_style)
                sheet.write((row+6), 13, round(total_base_imponible_contribuyente_8 + total_base_imponible_no_contribuyente_8 - total_nota_credito_8 - total_nota_debito_8,2), line_number)
                sheet.write((row+6), 14, total_iva_8, line_number)
                sheet.write((row+6), 15, 0, line_number)
                sheet.write((row+6), 16, '', line_number)
                sheet.merge_range('J%s:M%s' % (str(row+8), str(row+8)), 'Total Ventas Internas afectadas  más adicional 31.00', title_style)
                sheet.write((row+7), 13, round(total_base_imponible_contribuyente_31 + total_base_imponible_no_contribuyente_31 - total_nota_credito_31 - total_nota_debito_31,2), line_number)
                sheet.write((row+7), 14, total_iva_31, line_number)
                sheet.write((row+7), 15, 0, line_number)
                sheet.write((row+7), 16, '', line_number)
                sheet.merge_range('J%s:M%s' % (str(row+9), str(row+9)), 'Total Notas de Crédito o Devoluciones aplicadas en Ventas 16%', title_style)
                sheet.write((row+8), 13, total_nota_credito_16,line_number)
                sheet.write((row+8), 14, total_nota_credito_iva_16,line_number)
                sheet.write((row+8), 15, '',line_number)
                sheet.write((row+8), 16, '',line_number)
                sheet.merge_range('J%s:M%s' % (str(row+10), str(row+10)), 'Total Notas de Crédito o Devoluciones aplicadas en Ventas 8%', title_style)
                sheet.write((row+9), 13, total_nota_credito_8,line_number)
                sheet.write((row+9), 14, total_nota_credito_iva_8,line_number)
                sheet.write((row+9), 15, '',line_number)
                sheet.write((row+9), 16, '',line_number)
                sheet.merge_range('J%s:M%s' % (str(row+11), str(row+11)), 'Total Notas de Crédito o Devoluciones aplicadas en Ventas 31%', title_style)
                sheet.write((row+10), 13, total_nota_credito_31,line_number)
                sheet.write((row+10), 14, total_nota_credito_iva_31,line_number)
                sheet.write((row+10), 15, '',line_number)
                sheet.write((row+10), 16, '',line_number)
                sheet.merge_range('J%s:M%s' % (str(row+12), str(row+12)), 'Total Notas de Débito o recargos aplicadas en Ventas 16%:', title_style)
                sheet.write((row+11), 13, total_nota_debito_16,line_number)
                sheet.write((row+11), 14, total_nota_debito_iva_16,line_number)
                sheet.write((row+11), 15, '',line_number)
                sheet.write((row+11), 16, '',line_number)
                sheet.merge_range('J%s:M%s' % (str(row+13), str(row+13)), 'Total Notas de Débito o recargos aplicadas en Ventas 8%:', title_style)
                sheet.write((row+12), 13, total_nota_debito_8,line_number)
                sheet.write((row+12), 14, total_nota_debito_iva_8,line_number)
                sheet.write((row+12), 15, '',line_number)
                sheet.write((row+12), 16, '',line_number)
                sheet.merge_range('J%s:M%s' % (str(row+14), str(row+14)), 'Total Notas de Débito o recargos aplicadas en Ventas 31%:', title_style)
                sheet.write((row+13), 13, total_nota_debito_31,line_number)
                sheet.write((row+13), 14, total_nota_debito_iva_31,line_number)
                sheet.write((row+13), 15, '',line_number)
                sheet.write((row+13), 16, '',line_number)
                sheet.merge_range('J%s:M%s' % (str(row+15), str(row+15)), 'Total:', title_style)
                sheet.write((row+14), 13, total_base_exento_contribuyente + total_base_exento_no_contribuyente + total_base_imponible_contribuyente_16 + total_base_imponible_no_contribuyente_16\
                        + total_base_imponible_contribuyente_8 + total_base_imponible_no_contribuyente_8 \
                        + total_base_imponible_contribuyente_31 + total_base_imponible_no_contribuyente_31
                              + total_base_exento_credito \
                                    + total_base_exento_debito,line_number)
                sheet.write((row+14), 14, (total_iva_16 + total_iva_8 + total_iva_31 + \
                    total_nota_credito_iva_16 + total_nota_credito_iva_8 + total_nota_credito_iva_31 + \
                        total_nota_debito_iva_16 + total_nota_debito_iva_8 + total_nota_debito_iva_31),line_number)
                sheet.write((row+14), 15, total_iva_16_retenido,line_number)
                sheet.write((row+14), 16, total_igtf,line_number)

            # Totales de compras
            else:
                
                sheet.write((row), 12, c_total_base_exento, line_total)
                sheet.write((row), 16, c_total_base_imponible_16, line_total)
                sheet.write((row), 18, c_total_iva_16, line_total)
                sheet.write((row), 19, c_total_base_imponible_8, line_total)
                sheet.write((row), 21, c_total_iva_8, line_total)
                sheet.write((row), 22, c_total_base_imponible_31, line_total)
                sheet.write((row), 24, c_total_iva_31, line_total)
                sheet.write((row), 26, c_total_igtf, line_total)


                row += 5
                sheet.merge_range('J%s:M%s' % (str(row + 1), str(row + 1)), 'RESUMEN GENERAL', cell_format_2)
                sheet.write((row), 13, 'Base Imponible', cell_format_1)
                sheet.write((row), 14, 'Crédito  fiscal', cell_format_1)
                sheet.write((row), 15, 'IVA retenido por el comprador', cell_format_1)
                sheet.write((row), 16, 'IVA retenido a terceros', cell_format_1)
                sheet.write((row), 17, 'IGTF', cell_format_1)

                sheet.merge_range('J%s:M%s' % (str(row + 2), str(row + 2)), 'Total Compras Internas NO Gravadas',
                                  title_style)
                sheet.write((row + 1), 13, c_total_base_exento, line_number)
                sheet.write((row + 1), 14, 0, line_number)
                sheet.write((row + 1), 15, 0, line_number)
                sheet.write((row + 1), 16, 0, line_number)
                sheet.write((row + 1), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row + 3), str(row + 3)), 'Total Notas de Credito NO Gravadas',
                                  title_style)
                sheet.write((row + 2), 13, total_base_exento_credito, line_number)
                sheet.write((row + 2), 14, 0, line_number)
                sheet.write((row + 2), 15, 0, line_number)
                sheet.write((row + 2), 16, 0, line_number)
                sheet.write((row + 2), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row + 4), str(row + 4)), 'Total Notas de Debito NO Gravadas',
                                  title_style)
                sheet.write((row + 3), 13, total_base_exento_debito, line_number)
                sheet.write((row + 3), 14, 0, line_number)
                sheet.write((row + 3), 15, 0, line_number)
                sheet.write((row + 3), 16, 0, line_number)
                sheet.write((row + 3), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row + 5), str(row + 5)), 'Total Compras de Importaciòn', title_style)
                sheet.write((row + 4), 13, 0, line_number)
                sheet.write((row + 4), 14, 0, line_number)
                sheet.write((row + 4), 15, 0, line_number)
                sheet.write((row + 4), 16, 0, line_number)
                sheet.write((row + 4), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row + 6), str(row + 6)),
                                  'Total Compras Internas afectadas sólo alícuota general 16.00', title_style)
                sheet.write((row + 5), 13, round(c_total_base_imponible_16,2), line_number)
                sheet.write((row + 5), 14, c_total_iva_16, line_number)
                sheet.write((row + 5), 15, total_iva_16_retenido, line_number)
                sheet.write((row + 5), 16, total_iva_16_igtf, line_number)
                sheet.write((row + 5), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row + 7), str(row + 7)),
                                  'Total Compras Internas afectadas sólo alícuota reducida 8.00', title_style)
                sheet.write((row + 6), 13, c_total_base_imponible_8, line_number)
                sheet.write((row + 6), 14, c_total_iva_8, line_number)
                sheet.write((row + 6), 15, 0, line_number)
                sheet.write((row + 6), 16, 0, line_number)
                sheet.write((row + 6), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row + 8), str(row + 8)),
                                  'Total Compras Internas afectadas por alícuota general más adicional 31.00', title_style)
                sheet.write((row + 7), 13, c_total_base_imponible_31, line_number)
                sheet.write((row + 7), 14, c_total_iva_31, line_number)
                sheet.write((row + 7), 15, 0, line_number)
                sheet.write((row + 7), 16, 0, line_number)
                sheet.write((row + 7), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row+9), str(row+9)), 'Total Notas de Crédito o Devoluciones aplicadas en Compras 16%', title_style)
                sheet.write((row+8), 13, total_nota_credito_16, line_number)
                sheet.write((row+8), 14, total_nota_credito_iva_16, line_number)
                sheet.write((row+8), 15, 0, line_number)
                sheet.write((row+8), 16, 0, line_number)
                sheet.write((row + 8), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row+10), str(row+10)), 'Total Notas de Crédito o Devoluciones aplicadas en Compras 8%', title_style)
                sheet.write((row+9), 13, total_nota_credito_8, line_number)
                sheet.write((row+9), 14, total_nota_credito_iva_8, line_number)
                sheet.write((row+9), 15, 0, line_number)
                sheet.write((row+9), 16, 0, line_number)
                sheet.write((row + 9), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row+11), str(row+11)), 'Total Notas de Crédito o Devoluciones aplicadas en Compras 31%', title_style)
                sheet.write((row+10), 13, total_nota_credito_31, line_number)
                sheet.write((row+10), 14, total_nota_credito_iva_31, line_number)
                sheet.write((row+10), 15, 0, line_number)
                sheet.write((row+10), 16, 0, line_number)
                sheet.write((row + 10), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row+12), str(row+12)), 'Total Notas de Débito o recargos aplicadas en Compras 16%:', title_style)
                sheet.write((row+11), 13, total_nota_debito_16, line_number)
                sheet.write((row+11), 14, total_nota_debito_iva_16, line_number)
                sheet.write((row+11), 15, 0, line_number)
                sheet.write((row+11), 16, 0, line_number)
                sheet.write((row+11), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row+13), str(row+13)), 'Total Notas de Débito o recargos aplicadas en Compras 8%:', title_style)
                sheet.write((row+12), 13, total_nota_debito_8, line_number)
                sheet.write((row+12), 14, total_nota_debito_iva_8, line_number)
                sheet.write((row+12), 15, 0, line_number)
                sheet.write((row+12), 16, 0, line_number)
                sheet.write((row +12), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row+14), str(row+14)), 'Total Notas de Débito o recargos aplicadas en Compras 31%:', title_style)
                sheet.write((row+13), 13, total_nota_debito_31, line_number)
                sheet.write((row+13), 14, total_nota_debito_iva_31, line_number)
                sheet.write((row+13), 15, 0, line_number)
                sheet.write((row+13), 16, 0, line_number)
                sheet.write((row +13), 17, 0, line_number)
                sheet.merge_range('J%s:M%s' % (str(row+15), str(row+15)), 'Total:', title_style)
                sheet.write((row+14), 13, round(c_total_base_exento + c_total_base_imponible_16 \
                    + c_total_base_imponible_8+c_total_base_imponible_31+total_nota_credito_16+\
                        + total_nota_credito_8 + total_nota_credito_31 +total_nota_debito_16 + \
                            + total_nota_debito_8 + total_nota_debito_31 + total_base_exento_credito +\
                                total_base_exento_debito ,2), line_number)
                sheet.write((row+14), 14, (c_total_iva_16 + c_total_iva_8 + c_total_iva_31 + \
                    total_nota_credito_iva_16 + total_nota_credito_iva_8 + total_nota_credito_iva_31 + \
                        total_nota_debito_iva_16 + total_nota_debito_iva_8 + total_nota_debito_iva_31), line_number)
                sheet.write((row+14), 15, total_iva_16_retenido, line_number)
                sheet.write((row+14), 16, total_iva_16_igtf, line_number)
                sheet.write((row+14), 17, c_total_igtf, line_number)