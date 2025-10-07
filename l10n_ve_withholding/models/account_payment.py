# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2022-Present.
#
#
###############################################################################
from odoo import models, fields, api, _, Command
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    #created to record retention percentages
    comment_withholding = fields.Char(string='Comment withholding')
    concept_withholding = fields.Char(string='Concept withholding')
    withholding_distribution = fields.Boolean(
        string='tiene una distribucion de retencion?'
    )
    withholding_distribution_ids = fields.One2many(
        'withholding.distribution',
        'payment_id',
        string='distribucion de retencion'
    )
    withholding_distributin_islr = fields.Boolean(
        '¿Aplicar varios conceptos de ISLR?',
        default=False
    )
    withholding_distributin_islr_ids = fields.One2many(
        'withholding.distribution.islr',
        'payment_id',
        string='Distribucion de conceptos'
    )
    third_partner_withholding = fields.Boolean(
        string='Retención a terceros',
        default=False
    )
    third_partner_id = fields.Many2one(
        string=_('Tercero'),
        comodel_name='res.partner',
    )
    partner_regimen_islr_ids = fields.Many2many(
        'seniat.tabla.islr',
        compute='_compute_partner_regimenes_islr',
    )
    regimen_islr_id = fields.Many2one(
        'seniat.tabla.islr',
        'Aplicativo ISLR'
    )
    # this field is to be used by vat retention
    selected_debt_taxed = fields.Monetary(
        string='Selected Debt taxed',
        compute='_compute_selected_debt_taxed',
    )

    @api.depends(
        'partner_id.seniat_regimen_islr_ids',
        'third_partner_withholding',
        'third_partner_id.seniat_regimen_islr_ids')
    def _compute_partner_regimenes_islr(self):
        """
            Lo hacemos con campo computado y no related para que solo se setee
            y se exija si es pago a proveedor
        """
        for payment in self:
            if payment.partner_type == 'supplier':
                payment.partner_regimen_islr_ids = payment.partner_id.seniat_regimen_islr_ids
                if payment.third_partner_withholding and payment.third_partner_id and payment.partner_type == 'supplier':
                    payment.partner_regimen_islr_ids = payment.third_partner_id.seniat_regimen_islr_ids
            else:
                payment.partner_regimen_islr_ids = payment.env['seniat.tabla.islr']

    @api.depends(
        'to_pay_move_line_ids.amount_residual',
        'to_pay_move_line_ids.amount_residual_currency',
        'to_pay_move_line_ids.currency_id',
        'to_pay_move_line_ids.move_id',
        'date',
        'currency_id')
    def _compute_selected_debt_taxed(self):
        for payment in self:
            selected_debt_taxed = 0.0
            for line in payment.to_pay_move_line_ids._origin:
                #this is conditional used to vat retention
                for li in line.move_id.line_ids:
                    tax_list = [
                        self.env.ref('l10n_ve_base.tax8purchase').with_company(payment.company_id or self.env.company).id,
                        self.env.ref('l10n_ve_base.tax16purchase').id,
                        self.env.ref('l10n_ve_base.tax31purchase').id,
                    ]
                    if li.tax_line_id in tax_list:
                        if line.move_id.move_type == 'in_refund':
                            selected_debt_taxed += li.credit
                        else:
                            selected_debt_taxed += li.debit

            payment.selected_debt_taxed = selected_debt_taxed

    @api.onchange('withholding_distributin_islr')
    def _onchange_withholding_distributin_islr(self):
        for payment in self:
            withholding_distributin_islr_ids = []
            if payment.withholding_distributin_islr:
                to_pay = payment.to_pay_move_line_ids[0]
                if to_pay.move_id.invoice_line_ids:
                    for line in to_pay.move_id.invoice_line_ids:
                        if not line.product_id.product_tmpl_id.disable_islr:
                            withholding_distributin_islr_ids.append(Command.create({
                                'payment_id': payment.id,
                                'move_line_id': line.id,
                            }))
            payment.withholding_distributin_islr_ids = withholding_distributin_islr_ids

    def _get_fiscal_period(self, date):
        str_date = str(date).split('-')
        vals = 'AÑO '+str_date[0]+' MES '+str_date[1]
        return vals

    # @api.onchange('journal_id')
    # def _onchange_compute_amount_currency(self):
    #     for rec in self:
    #         pass
    #         if rec.other_currency and rec.payment_group_id:
    #             if rec.payment_group_id.payments_amount <= 0:
    #                 rec.amount = rec.payment_group_id.selected_finacial_debt
    #             if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
    #                 rec.amount = 0
    #                 payments_amount = rec.payment_group_id.selected_finacial_debt - \
    #                     rec.payment_group_id.payments_amount
    #                 rec.amount = rec.company_id.currency_id._convert(
    #                     payments_amount, rec.currency_id, rec.company_id, rec.date)
    #         if not rec.other_currency and rec.payment_group_id:
    #             rec.amount = rec.payment_group_id.selected_finacial_debt
    #             if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
    #                 payments_amount = rec.payment_group_id.payments_amount - rec.amount
    #                 rec.amount = rec.payment_group_id.selected_finacial_debt - \
    #                     payments_amount

    @api.onchange('date')
    def _onchange_compute_amount_currency_date(self):
        for payment in self:
            if payment.other_currency and payment.payment_group_id:
                payment.amount_company_currency = payment.currency_id._convert(
                    payment.amount,
                    payment.company_id.currency_id,
                    payment.company_id,
                    payment.date
                )

    def action_post(self):
        for pay in self:
            if pay.payment_group_id and pay.payment_group_id.to_pay_move_line_ids:
                to_pay = pay.payment_group_id.to_pay_move_line_ids[0]
                if to_pay.move_id.move_type == 'in_refund' and  pay.computed_withholding_amount:
                    pay.write({
                        'payment_type': 'inbound',
                    })
        return super(AccountPayment, self).action_post()

    def get_sustraendo(self):
        if self.concept_withholding:
            code_seniat = self.concept_withholding.split(' - ')[0]
            activity_name = self.concept_withholding.split(' - ')[1]
            regimen_id = self.env['seniat.tabla.islr'].search([
                ('code_seniat', '=', code_seniat),
                ('activity_name', '=', activity_name)
            ],limit=1)
            if regimen_id and regimen_id.type_subtracting == 'amount':
                return self.format_miles_number(
                    regimen_id.banda_calculo_ids[0].withholding_amount
                )
        return False

    def format_miles_number(self, number):
        return '{:,.2f}'.format(number).replace(",", "@").replace(".", ",").replace("@", ".")