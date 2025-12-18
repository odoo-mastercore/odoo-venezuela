# -*- coding: utf-8 -*-
############################################################################## # Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2022-Present.
#
#
###############################################################################
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    l10n_ve_withholding_islr = fields.Boolean(
        '¿Aplicar Retención ISLR?',
        default=False
    )
    l10n_ve_withholding_distribution_islr = fields.Boolean(
        '¿Aplicar varios conceptos de ISLR?',
        default=False
    )
    l10n_ve_third_partner_withholding = fields.Boolean(
        string='Retención a terceros',
        default=False
    )
    l10n_ve_third_partner_id = fields.Many2one(
        string='Tercero',
        comodel_name='res.partner',
    )
    l10n_ve_partner_regimen_islr_ids = fields.Many2many(
        'seniat.tabla.islr',
        compute='_compute_partner_regimenes_islr',
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
        auto_join=True
    )
    l10n_ve_withholdings_amount = fields.Monetary(
        compute="_compute_l10n_ve_withholdings_amount",
        currency_field="company_currency_id",
        string="Withholdings"
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
    def _compute_l10n_ve_withholding_line_ids(self):
        for rec in self.filtered(lambda x: x.partner_type == "supplier"):
            withholdings = []
            wth_islr = False
            if rec.partner_id.l10n_ve_partner_tax_ids:
                if any(x.tax_id.l10n_ve_tax_type == 'tabla_islr' for x in rec.partner_id.l10n_ve_partner_tax_ids):
                    wth_islr = True
                withholdings.extend([
                    Command.create({'tax_id': x.tax_id.id})
                    for x in rec.partner_id.l10n_ve_partner_tax_ids
                ])
            rec.l10n_ve_withholding_islr = wth_islr
            rec.l10n_ve_withholding_line_ids = withholdings

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
            company_id = payment.company_id.id if not payment.company_id.parent_id \
                else payment.company_id.parent_id.id
            tax_list = [
                self.env.ref(f'account.{company_id}_tax8purchase').id,
                self.env.ref(f'account.{company_id}_tax16purchase').id,
                self.env.ref(f'account.{company_id}_tax31purchase').id,
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
                amount_untaxed = line_to_pay.move_id.amount_untaxed
                if line_to_pay.move_id.currency_id != payment.company_id.currency_id:
                    amount_untaxed = line_to_pay.move_id.currency_id._convert(
                        line_to_pay.move_id.amount_untaxed,
                        payment.company_id.currency_id,
                        payment.company_id,
                        payment.date
                    )
                withholding_untaxed += amount_untaxed
            payment.l10n_ve_withholding_untaxed = withholding_untaxed

    @api.onchange("l10n_ve_withholdings_amount")
    def _onchange_withholdings(self):
        # con esto evitamos el importe negativo en pagos a proveedores
        for rec in self.filtered(lambda x: not x._is_latam_check_payment()):
            amount = rec.amount + rec.payment_difference
            rec.amount = amount if amount > 0 else 0

    @api.onchange('l10n_ve_withholding_islr')
    def _onchange_l10n_ve_withholding_islr(self):
        for payment in self:
            withholding_islr_ids = []
            if payment.l10n_ve_withholding_islr:
                to_pay = payment.to_pay_move_line_ids[0]
                tax_id = self.env['account.tax'].search([
                    ('l10n_ve_withholding_payment_type', '=', 'supplier'),
                    ('l10n_ve_tax_type', '=', 'tabla_islr')
                ], limit=1)
                if to_pay.move_id:
                    withholding_islr_ids.append(Command.create({
                        'tax_id': tax_id.id,
                        'payment_id': payment.id,
                        'calc_islr': 'all'
                    }))
            else:
                withholding_islr_ids = self._delete_islr_lines()
                payment.l10n_ve_withholding_distribution_islr = False
            payment.l10n_ve_withholding_line_ids = withholding_islr_ids

    def _delete_islr_lines(self):
        return [
            Command.delete(line.id)
            for line in self.l10n_ve_withholding_line_ids
            if line.l10n_ve_tax_type == 'tabla_islr'
        ]

    @api.onchange('l10n_ve_withholding_distribution_islr')
    def _onchange_l10n_ve_withholding_distribution_islr(self):
        for payment in self:
            withholding_islr_ids = []
            if payment.l10n_ve_withholding_distribution_islr:
                withholding_islr_ids = self._delete_islr_lines()
                to_pay = payment.to_pay_move_line_ids[0]
                tax_id = self.env['account.tax'].search([
                    ('l10n_ve_withholding_payment_type', '=', 'supplier'),
                    ('l10n_ve_tax_type', '=', 'tabla_islr')
                ], limit=1)
                if to_pay.move_id.invoice_line_ids:
                    for line in to_pay.move_id.invoice_line_ids:
                        if not line.product_id.product_tmpl_id.l10n_ve_disable_islr:
                            withholding_islr_ids.append(Command.create({
                                'tax_id': tax_id.id,
                                'payment_id': payment.id,
                                'move_line_id': line.id,
                                'calc_islr': 'line'
                            }))
            else:
                withholding_islr_ids = self._delete_islr_lines()
            payment.l10n_ve_withholding_line_ids = withholding_islr_ids
            if payment.l10n_ve_withholding_islr and not payment.l10n_ve_withholding_distribution_islr:
                payment._onchange_l10n_ve_withholding_islr()

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

    def _format_miles_number(self, number):
        return '{:,.2f}'.format(number).replace(",", "@").replace(".", ",").replace("@", ".")

    def action_post(self):
        for payment in self:
            if payment.to_pay_move_line_ids:
                # TODO: REVISAR
                to_pay = payment.to_pay_move_line_ids[0]
                if to_pay.move_id.move_type == 'in_refund' and payment.l10n_ve_withholdings_amount:
                    payment.write({
                        'payment_type': 'inbound',
                    })
                if to_pay.move_id:
                    # Relacionamos las retenciones con la factura para uso de reportes
                    wth_to_add = [
                        wth.id for wth in payment.l10n_ve_withholding_line_ids \
                            if wth.id not in to_pay.move_id.l10n_ve_withholding_ids.ids]
                    current_ids = to_pay.move_id.l10n_ve_withholding_ids.ids
                    all_ids = list(set(current_ids + wth_to_add))
                    to_pay.move_id.l10n_ve_withholding_ids = [Command.set(all_ids)]

                # Relacionamos los pagos a la factura (User Ux)
                # TODO: Revisar si esto es correcto y funcional
                to_pay.move_id.write({"matched_payment_ids": [Command.link(payment.id)]})
            commands = []
            for line in payment.l10n_ve_withholding_line_ids if self.partner_type == 'supplier' else []:
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
                    payment.l10n_ve_withholding_line_ids = commands
        res = super(AccountPayment, self).action_post()
        if self.l10n_ve_withholding_line_ids and self.matched_move_line_ids and self.payment_type == 'outbound':
            invoice_id = self.mapped('matched_move_line_ids.move_id').filtered(lambda m: m.move_type == 'in_invoice')
            if self.date != invoice_id.invoice_date:
                raise UserError(
                    _("Error de Retenciones\n\n"
                      "Lo sentimos, no es posible registrar un pago de retención con una fecha distinta a la de la factura asociada (**%s**).\n\n"
                      "**Alternativa de Solución:**\n"
                      "Puede registrar la transacción en dos partes:\n"
                      "1. Un pago por el monto exacto de la retención, utilizando la **fecha de la factura**.\n"
                      "2. Un segundo pago por el resto del monto (si aplica), utilizando la **fecha deseada**.")
                      % invoice_id.invoice_date.strftime('%Y-%m-%d')
                )
        return res

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        res = super()._prepare_move_line_default_vals(write_off_line_vals, force_balance=force_balance)
        res += self._prepare_witholding_write_off_vals()
        wth_amount = sum(self.l10n_ve_withholding_line_ids.mapped("amount"))
        conversion_rate = self.exchange_rate or 1.0
        valid_account_types = self._get_valid_payment_account_types()
        for line in res:
            account_id = self.env["account.account"].browse(line["account_id"])
            if account_id.account_type in valid_account_types:
                if self.payment_type == "inbound" and "credit" in line:
                    line["credit"] += wth_amount
                    if not self._use_counterpart_currency():
                        line["amount_currency"] -= wth_amount / conversion_rate
                elif self.payment_type == "outbound" and "debit" in line:
                    line["debit"] += wth_amount
                    if not self._use_counterpart_currency():
                        line["amount_currency"] += wth_amount / conversion_rate
        return res

    def _prepare_witholding_write_off_vals(self):
        self.ensure_one()
        write_off_line_vals = []
        conversion_rate = self.exchange_rate or 1.0
        sign = 1
        if self.payment_type == "outbound":
            sign = -1
        for line in self.l10n_ve_withholding_line_ids:
            __, account_id, tax_repartition_line_id, __ = line._tax_compute_all_helper()
            amount_currency = self.currency_id.round(line.amount / conversion_rate)
            write_off_line_vals.append(
                {
                    **self._get_withholding_move_line_default_values(),
                    "name": line.name,
                    "account_id": account_id,
                    "amount_currency": sign * amount_currency,
                    "balance": sign * line.amount,
                    "tax_base_amount": sign * line.base_amount,
                    "tax_repartition_line_id": tax_repartition_line_id,
                }
            )

        account_id = self.company_id.l10n_ve_tax_base_account_id.id
        if account_id:
            for base_amount in list(set(self.l10n_ve_withholding_line_ids.mapped("base_amount"))):
                withholding_lines = self.l10n_ve_withholding_line_ids.filtered(lambda x: x.base_amount == base_amount)
                nice_base_label = ",".join(withholding_lines.filtered("name").mapped("name"))
                base_amount = sign * base_amount
                base_amount_currency = self.currency_id.round(base_amount / conversion_rate)
                write_off_line_vals.append(
                    {
                        **self._get_withholding_move_line_default_values(),
                        "name": _("Base Ret: ") + nice_base_label,
                        "tax_ids": [Command.set(withholding_lines.mapped("tax_id").ids)],
                        "account_id": account_id,
                        "balance": base_amount,
                        "amount_currency": base_amount_currency,
                    }
                )
                write_off_line_vals.append(
                    {
                        **self._get_withholding_move_line_default_values(),  # Counterpart 0 operation
                        "name": _("Base Ret Cont: ") + nice_base_label,
                        "account_id": account_id,
                        "balance": -base_amount,
                        "amount_currency": -base_amount_currency,
                    }
                )

        return write_off_line_vals

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
