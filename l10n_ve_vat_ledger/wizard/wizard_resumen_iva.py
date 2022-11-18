##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from re import search
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from re import search
import json
# import time
import logging
import xlsxwriter
import io
from io import BytesIO
import pandas as pd
import shutil
import base64
import csv
import xlwt


class ResumenIVA(models.TransientModel):
    _name = 'resumen.iva'
    _description = 'Resumen I.V.A'

    resumen_iva_ids = fields.Many2many('account.vat.ledger', string='nuevo')
    content = fields.Binary('Content')
    date_from = fields.Date(string='Date From', default=lambda *a: datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a: (datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))


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

    # def generate_xls_report(self):
    def generate_xls_report(self, workbook, data, account_vat):
        for obj in account_vat:
            report_name = obj.name
            sheet = workbook.add_worksheet(report_name[:31])
            self.ensure_one()
            _log = BytesIO()
            wb = xlsxwriter.Workbook(_log, {'in_memory': True})
            buffer = io.BytesIO()
            writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
            workbook = writer.book

            # Resumen IVA
            sheet2 = workbook.add_worksheet()

            sheet.set_column(0, 0, 9)
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

            # Resume IVA
            sheet2.set_column(7, 1, 20)

            sheet2.merge_range('A1:D1', obj.company_id.name, title_style)
            # sheet2.merge_range('A2:D2', obj.company_id.vat, title_style)
            # sheet2.merge_range('A3:G3', obj.name + ' ' + 'Libro de IVA Compras' + ' ' + 'mes' + ' ' + 'Año', title_style)

            # DEBITOS FISCALES
            sheet2.merge_range('A7:D7', 'DEBITOS FISCALES', title_style)
            sheet2.merge_range('A8:D8', 'Total Ventas Internas No Gravadas ', title_style)
            sheet2.merge_range('A9:D9', 'Total Ventas de Exportación  ', title_style)
            sheet2.merge_range('A10:D10', 'Total Ventas Internas afectadas sólo alícuota general 16.00 ', title_style)
            sheet2.merge_range('A11:D11', 'Total Ventas Internas afectadas sólo alícuota reducida 8.00 ', title_style)
            sheet2.merge_range('A12:D12', 'Total Ventas Internas afectadas por alícuota general más adicional 31.00 ',
                               title_style)
            sheet2.merge_range('A13:D13', 'Total Notas de Crédito o Devoluciones aplicadas en Ventas ', title_style)
            sheet2.merge_range('A14:D14', 'Total Notas de Débito o recargos aplicadas en Ventas ', title_style)
            sheet2.merge_range('A15:D15', 'Total de Dèbitos Fiscales ', title_style)
            sheet2.merge_range('A16:D16', 'Total IGTF Percibido ', title_style)

            # CREDITOS FISCALES
            sheet2.merge_range('A19:D19', 'Total Compras Internas No Gravadas ', title_style)
            sheet2.merge_range('A20:D20', 'Total Compras de Importaciòn', title_style)
            sheet2.merge_range('A21:D21', 'Total Compras  Internas afectadas sólo alícuota general 16.00 ', title_style)
            sheet2.merge_range('A22:D22', 'Total Compras Internas afectadas sólo alícuota reducida 8.00 ', title_style)
            sheet2.merge_range('A23:D23', 'Total Compras Internas afectadas por alícuota general más adicional 31.00',
                               title_style)
            sheet2.merge_range('A24:D24', 'Total Notas de Crédito aplicadas en Compras', title_style)
            sheet2.merge_range('A25:D25', 'Total Notas de Débito  aplicadas en Compras ', title_style)
            sheet2.merge_range('A26:D26', 'Total de Crèditos Fiscales ', title_style)
            sheet2.merge_range('A27:D27', 'Total IGTF Pagado', title_style)

            # AUTOLIQUIDACION
            sheet2.merge_range('A30:D30', 'AUTOLIQUIDACION', title_style)
            sheet2.merge_range('A31:D31', 'Total Cuota Tributaria ', title_style)
            sheet2.merge_range('A32:D32', 'Excedente de Crèdito Fiscal para el mes Siguiente', title_style)
            sheet2.merge_range('A33:D33', 'Retenciones Acumuladas por Descontar ', title_style)
            sheet2.merge_range('A34:D34', 'Retenciones del Perìodo', title_style)
            sheet2.merge_range('A35:D35', 'Total Retenciones', title_style)
            sheet2.merge_range('A36:D36', 'Retenciones del IVA Soportadas y Descontadas', title_style)
            sheet2.merge_range('A37:D37', 'Saldos de Retenciones del IVA no Aplicadas', title_style)
            sheet2.merge_range('A38:D38', 'Total a Pagar', title_style)



            # (primer numero celdas hacia abajo, segundo numero columnas de lado )
            sheet2.write(6, 5, 'Base Imponible', title_style)
            sheet2.write(7, 5, ' 0 ', title_style)
            sheet2.write(8, 5, ' 1 ', title_style)
            sheet2.write(9, 5, ' 2 ', title_style)
            sheet2.write(10, 5, ' 3 ', title_style)
            sheet2.write(11, 5, ' 4 ', title_style)
            sheet2.write(12, 5, ' 5 ', title_style)
            sheet2.write(13, 5, ' 6 ', title_style)
            sheet2.write(14, 5, ' 7 ', title_style)
            sheet2.write(15, 5, ' 8 ', title_style)

            sheet2.write(6, 6, 'Dèbito Fiscal', title_style)
            sheet2.write(7, 6, ' 0 ', title_style)
            sheet2.write(8, 6, ' 1 ', title_style)
            sheet2.write(9, 6, ' 2 ', title_style)
            sheet2.write(10, 6, ' 3 ', title_style)
            sheet2.write(11, 6, ' 4 ', title_style)
            sheet2.write(12, 6, ' 5 ', title_style)
            sheet2.write(13, 6, ' 6 ', title_style)
            sheet2.write(14, 6, ' 7 ', title_style)
            sheet2.write(15, 6, ' 8 ', title_style)

            # (primer numero celdas hacia abajo, segundo numero columnas de lado )
            sheet2.write(18, 5, 'Base Imponible', title_style)
            sheet2.write(19, 5, ' 0 ', title_style)
            sheet2.write(20, 5, ' 1 ', title_style)
            sheet2.write(21, 5, ' 2 ', title_style)
            sheet2.write(22, 5, ' 3 ', title_style)
            sheet2.write(23, 5, ' 4 ', title_style)
            sheet2.write(24, 5, ' 5 ', title_style)
            sheet2.write(25, 5, ' 6 ', title_style)
            sheet2.write(26, 5, ' 7 ', title_style)

            sheet2.write(18, 6, 'Dèbito Fiscal', title_style)
            sheet2.write(19, 6, ' 0 ', title_style)
            sheet2.write(20, 6, ' 1 ', title_style)
            sheet2.write(21, 6, ' 2 ', title_style)
            sheet2.write(22, 6, ' 3 ', title_style)
            sheet2.write(23, 6, ' 4 ', title_style)
            sheet2.write(24, 6, ' 5 ', title_style)
            sheet2.write(25, 6, ' 6 ', title_style)
            sheet2.write(26, 6, ' 7 ', title_style)

            # (primer numero celdas hacia abajo, segundo numero columnas de lado )
            # sheet2.write(18, 6, 'Dèbito Fiscal', title_style)
            sheet2.write(30, 6, ' 0 ', title_style)
            sheet2.write(31, 6, ' 1 ', title_style)
            sheet2.write(32, 6, ' 2 ', title_style)
            sheet2.write(33, 6, ' 3 ', title_style)
            sheet2.write(34, 6, ' 4 ', title_style)
            sheet2.write(35, 6, ' 5 ', title_style)
            sheet2.write(36, 6, ' 6 ', title_style)
            sheet2.write(37, 6, ' 7 ', title_style)

            # Guardando en local el Excel generado
            writer.save()
            wb.close()
            buffer.seek(0)
            content = buffer.read()
            buffer.close()

            self.write({'content': base64.encodebytes(content)})
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model={}&field=content&download=true&id={}&filename=Resumen_IVA.xlsx'.format(
                    self._name, self.id, self.date_from, self.date_to),

        }