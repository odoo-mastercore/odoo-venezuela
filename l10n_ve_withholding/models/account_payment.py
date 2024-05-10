# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2022-Present.
#
#
###############################################################################
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    #created to record retention percentages
    comment_withholding = fields.Char('Comment withholding')
    concept_withholding = fields.Char('Concept withholding')
    withholding_distribution_ids = fields.One2many(
        'withholding.distribution', 'payment_id',
        string='distribucion de retencion'
    )
    withholding_number_state = fields.Boolean(string=_('Número de retención editable'),
        compute="_compute_withholding_number_readonly")

    @api.depends('payment_type','state')
    def _compute_withholding_number_readonly(self):
        for rec in self:
            state = True
            if rec.payment_type == 'inbound' and rec.state == 'draft':
                state = False
            return state

    def _get_fiscal_period(self, date):
        str_date = str(date).split('-')
        vals = 'AÑO '+str_date[0]+' MES '+str_date[1]
        return vals

    @api.onchange('journal_id')
    def _onchange_compute_amount_currency(self):
        for rec in self:
            pass
            if rec.other_currency and rec.payment_group_id:
                if rec.payment_group_id.payments_amount <= 0:
                    rec.amount = rec.payment_group_id.selected_finacial_debt
                if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
                    rec.amount = 0
                    payments_amount = rec.payment_group_id.selected_finacial_debt - \
                        rec.payment_group_id.payments_amount
                    rec.amount = rec.company_id.currency_id._convert(
                        payments_amount, rec.currency_id, rec.company_id, rec.date)
            if not rec.other_currency and rec.payment_group_id:
                rec.amount = rec.payment_group_id.selected_finacial_debt
                if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
                    payments_amount = rec.payment_group_id.payments_amount - rec.amount
                    rec.amount = rec.payment_group_id.selected_finacial_debt - \
                        payments_amount

    @api.onchange('date')
    def _onchange_compute_amount_currency_date(self):
        for rec in self:
            if rec.other_currency and rec.payment_group_id:
                rec.amount_company_currency = rec.currency_id._convert(
                    rec.amount, rec.company_id.currency_id,
                    rec.company_id, rec.date)

    def _create_paired_internal_transfer_payment(self):
        ''' When an internal transfer is posted, a paired payment is created
        with opposite payment_type and swapped journal_id & destination_journal_id.
        Both payments liquidity transfer lines are then reconciled.
        '''
        for payment in self:
            paired_payment = payment.copy({
                'journal_id': payment.destination_journal_id.id,
                'destination_journal_id': payment.journal_id.id,
                'payment_type': payment.payment_type == 'outbound' and 'inbound' or 'outbound',
                'move_id': None,
                'ref': payment.ref,
                'paired_internal_transfer_payment_id': payment.id,
                'date': payment.date,
                'exchange_rate': payment.exchange_rate,
                'amount_company_currency': payment.amount_company_currency,
            })
            paired_payment.move_id._post(soft=False)
            payment.paired_internal_transfer_payment_id = paired_payment

            body = _('This payment has been created from <a href=# data-oe-model=account.payment data-oe-id=%d>%s</a>') % (
                payment.id, payment.name)
            paired_payment.message_post(body=body)
            body = _('A second payment has been created: <a href=# data-oe-model=account.payment data-oe-id=%d>%s</a>') % (
                paired_payment.id, paired_payment.name)
            payment.message_post(body=body)

            lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
            lines.reconcile()

    def action_post(self):
        for pay in self:
            if pay.payment_group_id and pay.payment_group_id.to_pay_move_line_ids:
                to_pay = pay.payment_group_id.to_pay_move_line_ids[0]
                if to_pay.move_id.move_type == 'in_refund' and  pay.computed_withholding_amount:
                    pay.write({
                        'payment_type': 'inbound',
                    })
        return super(AccountPayment, self).action_post()
