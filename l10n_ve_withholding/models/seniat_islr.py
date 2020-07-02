###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class SeniatUnidadTributaria(models.Model):
    _name = 'seniat.ut'
    _description = 'Modelo para registrar el valor de la Unidad Tributaria'
    _rec_name = 'amount'

    date = fields.Date(
        'Fecha',
        required=True,
    )
    amount = fields.Float(
        'Valor de la Unidad',
        required=True,
    )
    ref = fields.Text(
        'Referencia de la gaceta',
        required=True,
    )
    
class SeniatTipoPersonaISLR(models.Model):
    _name = 'seniat.partner.type'
    _description = 'Tipo de persona a aplicar la retención ISLR'

    name = fields.Char(
        'Nombre Persona',
        required=True,
    )
    code = fields.Char(
        'Abreviado',
        required=True,
    )

class SeniatFactor(models.Model):
    _name = 'seniat.factor'
    _description = 'Modelo para registrar el valor del factor de calculo ISLR'
    _rec_name = 'amount'

    date = fields.Date(
        'Fecha',
        required=True,
    )
    amount = fields.Float(
        'Valor del factor',
        required=True,
    )

class BandaCaculo(models.Model):
    _name = 'banda.calculo'
    _description = 'Modelo para registrar la banda de calculo del ISLR'
    _rec_name = 'complete_percentage'

    amount_minimum = fields.Float(
        'Monto mayor a ',
        help="Monto para expresar la cantidad que no entra a retención"
    )
    amount_maximum = fields.Float(
        'Monto menor a ',
        help="Monto para expresar la cantidad que no entra a retención"
    )
    type_amount = fields.Selection([
        ('ut', 'Unidad Tributaria'),
        ('bs', 'Bolivares'),
    ], 'Tipo de monto',
        help='Tipo por el cual expresan los montos minimos o maximos'
    )
    withholding_percentage = fields.Float(
        'Porcentaje de retención',
        help='% Base Retención'
    )
    withholding_amount = fields.Float(
        'Monto fijo de retención',
        help='Monto Retención'
    )
    complete_percentage = fields.Char(
        'Porcentaje de retención',
        compute='_compute_complete_percentage', 
    )
    type_subtracting_rel = fields.Selection([
        ('no_amount', 'Sin Sustraendo'),
        ('amount', 'Con Sustraendo'),
        ], 'Tipo Calculo'
    )

    @api.depends('withholding_percentage')
    def _compute_complete_percentage(self):
        for rec in self:
            rec.complete_percentage = str(rec.withholding_percentage)+'%'


class SeniatTablaIslr(models.Model):
    _name = 'seniat.tabla.islr'
    _description = 'Modelo para registrar los argumentos de calculo ISLR'
    _rec_name = 'complete_name'

    code_seniat = fields.Char(
        'Código SENIAT',
        size=6,
        required=True,
        help='Código del régimen de retención del ISLR.'
    )
    activity_name = fields.Char(
        'Actividad',
        required=True,
        help='Actividad para Archivo XML - Según Manual Seniat'
    )
    seniat_partner_type_id = fields.Many2one(
        'seniat.partner.type', 
        'Tipo de persona'
    )
    factor_id = fields.Many2one(
        'seniat.factor', 
        'Factor Calculo',
    )
    withholding_base_percentage = fields.Float(
        'Porcentaje Base de retención',
        help='% Base Retención'
    )
    type_subtracting = fields.Selection([
        ('no_amount', 'Sin Sustraendo'),
        ('amount', 'Con Sustraendo'),
        ], 'Tipo Calculo'
    )
    banda_calculo_ids = fields.Many2many(
        'banda.calculo',
        'seniat_tabla_islr_banda_rel',
        'seniat_tabla_islr_id', 'banda_calculo_id' ,
        string='Banda de calculo',
        help='Banda de calculo para la retención del ISLR'
    )
    complete_name = fields.Char(
        'Código SENIAT',
        compute='_compute_complete_name',
    )
    seniat_ut_id = fields.Many2one(
        'seniat.ut', 
        'Valor Unidad Tributaria'
    )

    @api.depends('code_seniat', 'activity_name')
    def _compute_complete_name(self):
        for rec in self:
            rec.complete_name = '%s - %s' % (
                rec.code_seniat, rec.activity_name)
