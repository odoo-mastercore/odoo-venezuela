# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2022-Present.
#
#
###############################################################################
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    l10n_ve_comment_withholding = fields.Char(string='Comment withholding')
    l10n_ve_concept_withholding = fields.Char(string='Concept withholding')
    l10n_ve_withholding_distribution = fields.Boolean(
        string='tiene una distribucion de retencion?'
    )
    l10n_ve_withholding_distribution_ids = fields.One2many(
        'withholding.distribution',
        'payment_id',
        string='distribucion de retencion'
    )
    l10n_ve_withholding_distributin_islr = fields.Boolean(
        '¿Aplicar varios conceptos de ISLR?',
        default=False
    )
    l10n_ve_withholding_distributin_islr_ids = fields.One2many(
        'withholding.distribution.islr',
        'payment_id',
        string='Distribucion de conceptos'
    )
    l10n_ve_third_partner_withholding = fields.Boolean(
        string='Retención a terceros',
        default=False
    )
    l10n_ve_third_partner_id = fields.Many2one(
        string=_('Tercero'),
        comodel_name='res.partner',
    )
    l10n_ve_partner_regimen_islr_ids = fields.Many2many(
        'seniat.tabla.islr',
        compute='_compute_partner_regimenes_islr',
    )
    l10n_ve_regimen_islr_id = fields.Many2one(
        'seniat.tabla.islr',
        'Aplicativo ISLR'
    )
    # this field is to be used by vat retention
    l10n_ve_withholding_taxed = fields.Monetary(
        string='Withholding taxed',
        compute='_compute_l10n_ve_withholding_taxed',
    )
    l10n_ve_withholding_untaxed = fields.Monetary(
        string='Selected Debt untaxed',
        compute='_compute_l10n_ve_withholding_untaxed',
    )
    l10n_ve_move_line_taxes_ids = fields.Many2many(
        string='Withholding move line taxes',
        comodel_name='account.move.line',
        relation='move_account_payment_wth_line_rel',
        column1='move_line_id',
        column2='payment_id',
    )
    l10n_ve_withholdable_advanced_amount = fields.Monetary(
        "Adjustment / Advance (untaxed)",
        help="Used for withholdings calculation",
        currency_field="company_currency_id",
        compute="_compute_withholdable_advanced_amount",
        copy=False,
        store=True,
        readonly=False,
    )
    l10n_ve_withholding_line_ids = fields.One2many(
        "l10n_ve.payment.withholding",
        "payment_id",
        string="Withholdings Lines",
        compute="_compute_l10n_ve_withholding_line_ids",
        readonly=False,
        store=True,
    )
    l10n_ve_withholdings_amount = fields.Monetary(
        compute="_compute_l10n_ve_withholdings_amount",
        currency_field="company_currency_id",
    )

    @api.constrains("currency_id", "company_id", "l10n_ve_withholding_line_ids")
    def _check_withholdings_and_currency(self):
        for rec in self:
            if rec.l10n_ve_withholding_line_ids and rec.currency_id != rec.company_id.currency_id:
                raise UserError(_('Withholdings must be done in "%s" currency') % rec.company_id.currency_id.name)

    @api.depends("l10n_ve_withholding_line_ids.amount")
    def _compute_payment_total(self):
        super()._compute_payment_total()
        for rec in self:
            rec.payment_total += sum(rec.l10n_ve_withholding_line_ids.mapped("amount"))

    @api.depends("partner_id", "company_id", "date")
    def _compute_l10n_ar_withholding_line_ids(self):
        # metodo completamente analogo a payment.register._compute_l10n_ar_withholding_ids
        for rec in self.filtered(lambda x: x.partner_type == "supplier"):
            withholdings = [Command.clear()]
            if rec.partner_id.l10n_ve_partner_tax_ids:
                partner_taxes = self.env['l10n_ve.partner.tax'].search([
                    *self.env['l10n_ve.partner.tax']._check_company_domain(rec.company_id),
                    ('partner_id', '=', rec.partner_id.commercial_partner_id.id),
                    ('tax_id.l10n_ve_withholding_payment_type', '=', rec.partner_type)
                ])
                withholdings.append([Command.create({'tax_id': x.tax_id.id}) for x in partner_taxes])
            rec.l10n_ar_withholding_line_ids = withholdings

    @api.depends("l10n_ve_withholding_line_ids.amount")
    def _compute_l10n_ve_withholdings_amount(self):
        for payment in self:
            payment.l10n_ve_withholdings_amount = sum(payment.l10n_ve_withholding_line_ids.mapped("amount"))

    @api.depends("unreconciled_amount")
    def _compute_withholdable_advanced_amount(self):
        for rec in self:
            rec.l10n_ve_withholdable_advanced_amount = rec.unreconciled_amount

    @api.depends(
        'partner_id.l10n_ve_seniat_regimen_islr_ids',
        'l10n_ve_third_partner_withholding',
        'l10n_ve_third_partner_id.l10n_ve_seniat_regimen_islr_ids')
    def _compute_partner_regimenes_islr(self):
        """
            Lo hacemos con campo computado y no related para que solo se setee
            y se exija si es pago a proveedor
        """
        for payment in self:
            if payment.partner_type == 'supplier':
                payment.l10n_ve_partner_regimen_islr_ids = payment.partner_id.l10n_ve_seniat_regimen_islr_ids
                if payment.l10n_ve_third_partner_withholding and payment.l10n_ve_third_partner_id and payment.partner_type == 'supplier':
                    payment.l10n_ve_partner_regimen_islr_ids = payment.l10n_ve_third_partner_id.l10n_ve_seniat_regimen_islr_ids
            else:
                payment.l10n_ve_partner_regimen_islr_ids = payment.env['seniat.tabla.islr']

    @api.depends(
        'to_pay_move_line_ids.amount_residual',
        'to_pay_move_line_ids.amount_residual_currency',
        'to_pay_move_line_ids.currency_id',
        'to_pay_move_line_ids.move_id',
        'date',
        'currency_id')
    def _compute_l10n_ve_withholding_taxed(self):
        for payment in self:
            withholding_taxed = 0.0
            move_line_tax_ids = []
            tax_list = [
                self.env.ref(f'account.{payment.company_id.id}_tax8purchase').id,
                self.env.ref(f'account.{payment.company_id.id}_tax16purchase').id,
                self.env.ref(f'account.{payment.company_id.id}_tax31purchase').id,
            ]
            for line_to_pay in payment.to_pay_move_line_ids._origin:
                for move_line in line_to_pay.move_id.line_ids.filtered(lambda l: l.tax_line_id):
                    if move_line.tax_line_id.id in tax_list:
                        if line_to_pay.move_id.move_type == 'in_refund':
                            withholding_taxed += move_line.credit
                        else:
                            withholding_taxed += move_line.debit
                        move_line_tax_ids.append(move_line.id)
            payment.l10n_ve_withholding_taxed = withholding_taxed
            payment.l10n_ve_move_line_taxes_ids = [Command.set(move_line_tax_ids)]

    @api.depends(
        'to_pay_move_line_ids.move_id.amount_untaxed',
        'to_pay_move_line_ids.currency_id',
        'to_pay_move_line_ids.move_id',
        'date',
        'currency_id')
    def _compute_l10n_ve_withholding_untaxed(self):
        for payment in self:
            withholding_untaxed = 0.0
            for line_to_pay in payment.to_pay_move_line_ids._origin:
                withholding_untaxed += line_to_pay.move_id.amount_untaxed
            payment.l10n_ve_withholding_untaxed = withholding_untaxed

    @api.onchange("l10n_ve_withholdings_amount")
    def _onchange_withholdings(self):
        # con esto evitamos el importe negativo en pagos a proveedores
        for rec in self.filtered(lambda x: x.partner_type == "supplier" and not x._is_latam_check_payment()):
            amount = rec.amount + rec.payment_difference
            rec.amount = amount if amount > 0 else 0

    @api.onchange('l10n_ve_withholding_distributin_islr')
    def _onchange_l10n_ve_withholding_distributin_islr(self):
        for payment in self:
            withholding_distributin_islr_ids = []
            if payment.l10n_ve_withholding_distributin_islr:
                to_pay = payment.to_pay_move_line_ids[0]
                if to_pay.move_id.invoice_line_ids:
                    for line in to_pay.move_id.invoice_line_ids:
                        if not line.product_id.product_tmpl_id.l10n_ve_disable_islr:
                            withholding_distributin_islr_ids.append(Command.create({
                                'payment_id': payment.id,
                                'move_line_id': line.id,
                            }))
            payment.l10n_ve_withholding_distributin_islr_ids = withholding_distributin_islr_ids

    @api.model
    def _get_trigger_fields_to_synchronize(self):
        res = super()._get_trigger_fields_to_synchronize()
        return res + ("l10n_ve_withholding_line_ids",)

    def _get_withholding_move_line_default_values(self):
        return {
            "currency_id": self.currency_id.id,
        }

    def _get_fiscal_period(self, date):
        str_date = str(date).split('-')
        vals = 'AÑO '+str_date[0]+' MES '+str_date[1]
        return vals

    def _get_sustraendo(self):
        if self.l10n_ve_concept_withholding:
            code_seniat = self.l10n_ve_concept_withholding.split(' - ')[0]
            activity_name = self.l10n_ve_concept_withholding.split(' - ')[1]
            regimen_id = self.env['seniat.tabla.islr'].search([
                ('code_seniat', '=', code_seniat),
                ('activity_name', '=', activity_name)
            ],limit=1)
            if regimen_id and regimen_id.type_subtracting == 'amount':
                return self._format_miles_number(
                    regimen_id.banda_calculo_ids[0].withholding_amount
                )
        return False

    def _format_miles_number(self, number):
        return '{:,.2f}'.format(number).replace(",", "@").replace(".", ",").replace("@", ".")

    def action_post(self):
        for payment in self:
            if payment.to_pay_move_line_ids:
                # TODO: REVISAR
                to_pay = payment.to_pay_move_line_ids[0]
                if to_pay.move_id.move_type == 'in_refund' and payment.l10n_ve_withholding_amount:
                    payment.write({
                        'payment_type': 'inbound',
                    })
            commands = []
            for line in payment.l10n_ve_withholding_line_ids:
                if not line.name or line.name == "/":
                    if line.tax_id.l10n_ve_withholding_sequence_id:
                        commands.append(
                            Command.update(
                                line.id,
                                {
                                    "name": line.tax_id.l10n_ve_withholding_sequence_id.next_by_id()
                                    if line.amount
                                    else "/"
                                },
                            )
                        )
                    else:
                        raise UserError(
                            _("Please enter withholding number for tax %s or configure a sequence on that tax")
                            % line.tax_id.name
                        )
                if commands:
                    payment.l10n_ar_withholding_line_ids = commands
        return super(AccountPayment, self).action_post()

    # TODO: Aplicar en ext para multimonedas
    #This field is to be used by invoice in multicurrency
    # selected_finacial_debt = fields.Monetary(
    #     string='Selected Financial Debt',
    #     compute='_compute_selected_debt_financial',
    # )
    # selected_finacial_debt_currency = fields.Monetary(
    #     string='Selected Financial Debt in foreign currency',
    #     compute='_compute_selected_debt_financial',
    # )
    # debt_multicurrency = fields.Boolean(
    #     string='debt is in foreign currency?', default=False,
    # )
    # selected_debt_currency_id = fields.Many2one("res.currency",
    #     string='Selected Debt in foreign currency',
    # )

    # @api.depends(
    #     'to_pay_move_line_ids.amount_residual',
    #     'to_pay_move_line_ids.amount_residual_currency',
    #     'to_pay_move_line_ids.currency_id',
    #     'to_pay_move_line_ids.move_id',
    #     'payment_date',
    #     'currency_id',
    #     'partner_id',
    #     'selected_debt',
    # )
    # def _compute_selected_debt_financial(self):
    #     for rec in self:
    #         selected_finacial_debt = 0.0
    #         selected_finacial_debt_currency = 0.0
    #         for line in rec.to_pay_move_line_ids._origin:
    #             # factor for total_untaxed
    #             if line.move_id.currency_id.id != rec.company_id.currency_id.id:
    #                 selected_finacial_debt_currency += line.amount_residual_currency
    #                 rec.debt_multicurrency = True
    #                 rec.selected_debt_currency_id = line.move_id.currency_id.id
    #             elif line.move_id.currency_id.id != rec.company_id.currency_id.id and rec.debt_multicurrency:
    #                 selected_finacial_debt_currency += line.amount_residual_currency
    #                 rec.debt_multicurrency = True
    #             else:
    #                 rec.debt_multicurrency = False
    #             if rec.debt_multicurrency:
    #                 last_rate = 0
    #                 last_rate = self.env['res.currency.rate'].search([
    #                     ('currency_id', '=', rec.selected_debt_currency_id.id),
    #                     ('name', '=', rec.payment_date)
    #                 ], limit=1).rate
    #                 if last_rate == 0:
    #                     last_rate = self.env['res.currency.rate'].search([
    #                         ('currency_id', '=', rec.selected_debt_currency_id.id),
    #                     ], limit=1).rate
    #                 if last_rate == 0:
    #                     last_rate = 1
    #                 rate = round((1 / last_rate), 4)
    #                 finacial_debt_currency = selected_finacial_debt_currency*rate
    #                 selected_finacial_debt += finacial_debt_currency
    #             else:
    #                 selected_finacial_debt += line.amount_residual
    #                 #selected_debt += line.move_id.amount_residual
    #         sign = rec.partner_type == 'supplier' and -1.0 or 1.0
    #         rec.selected_finacial_debt = selected_finacial_debt * sign
    #         rec.selected_finacial_debt_currency = selected_finacial_debt_currency * sign

    # @api.depends('selected_debt', 'debt_multicurrency','selected_finacial_debt', 'unreconciled_amount',)
    # def _compute_to_pay_amount(self):
    #     for rec in self:
    #         if rec.selected_finacial_debt != rec.selected_debt:
    #             rec.to_pay_amount = rec.selected_finacial_debt + rec.unreconciled_amount
    #         else:
    #             rec.to_pay_amount = rec.selected_debt + rec.unreconciled_amount

    # @api.onchange('to_pay_amount')
    # def _inverse_to_pay_amount(self):
    #     for rec in self:
    #         if rec.selected_finacial_debt != rec.selected_debt:
    #             rec.unreconciled_amount = rec.to_pay_amount - rec.selected_finacial_debt
    #         else:
    #             rec.unreconciled_amount = rec.to_pay_amount - rec.selected_debt

    # por ahora no nos funciona computarlas, se duplica el importe. Igual conceptualemnte el onchange acá por ahí
    # está bien porque en realidad es una "sugerencia" actualizar el amount al usuario
    # @api.depends('withholdings_amount')
    # def _compute_amount(self):
    #     latam_checks = self.filtered(lambda x: x._is_latam_check_payment())
    #     super(AccountPayment, latam_checks)._compute_amount()
    #     for rec in (self - latam_checks):