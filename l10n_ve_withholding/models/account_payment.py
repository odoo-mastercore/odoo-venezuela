# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
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
            if (
                not rec._get_l10n_ve_active_withholding_lines()
                or rec.currency_id == rec.company_id.currency_id
            ):
                continue
            currency_data = rec._get_withholding_foreign_currency_data()
            compatible_foreign_currency = (
                currency_data and currency_data["currency"] == rec.currency_id
            )
            if not compatible_foreign_currency:
                raise UserError(_('Withholdings must be done in "%s" currency') % rec.company_id.currency_id.name)

    def _get_l10n_ve_active_withholding_lines(self):
        return self.l10n_ve_withholding_line_ids.filtered(
            lambda withholding: withholding.state != 'cancel'
        )

    @api.depends("l10n_ve_withholding_line_ids.amount", "l10n_ve_withholding_line_ids.state")
    def _compute_payment_total(self):
        super()._compute_payment_total()
        for rec in self:
            rec.payment_total += sum(rec._get_l10n_ve_active_withholding_lines().mapped("amount"))

    def _get_l10n_ve_partner_withholding_taxes(self):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        company = self.company_id
        company_ids = (company | company.parent_id).ids
        return partner.l10n_ve_partner_tax_ids.filtered(
            lambda tax: tax.tax_id.l10n_ve_withholding_payment_type == 'supplier'
            and tax.company_id.id in company_ids
        )

    def _get_l10n_ve_to_pay_moves(self):
        self.ensure_one()
        lines = self.to_pay_move_line_ids._origin or self.to_pay_move_line_ids
        return lines.mapped('move_id')

    def _move_has_l10n_ve_withholding_tax(self, move, tax):
        self.ensure_one()
        if not move or not tax:
            return False
        withholdings = move.l10n_ve_withholding_ids.filtered(
            lambda withholding: withholding.payment_id != self
            and withholding.state != 'cancel'
        )
        return tax.id in withholdings.tax_id.ids

    def _get_l10n_ve_moves_without_withholding_tax(self, tax):
        self.ensure_one()
        moves = self._get_l10n_ve_to_pay_moves()
        if not moves or not tax:
            return moves
        return moves.filtered(
            lambda move: not self._move_has_l10n_ve_withholding_tax(move, tax)
        )

    def _has_l10n_ve_moves_without_withholding_tax(self, tax):
        self.ensure_one()
        moves = self._get_l10n_ve_to_pay_moves()
        return bool(moves) and bool(self._get_l10n_ve_moves_without_withholding_tax(tax))

    def _allow_l10n_ve_auto_withholding(self):
        self.ensure_one()
        auto_move_ids = self.env.context.get('l10n_ve_auto_withhold_move_ids')
        if not auto_move_ids:
            return False
        auto_moves = self.env['account.move'].browse(auto_move_ids)
        return bool(auto_moves & self._get_l10n_ve_to_pay_moves())

    def _prepare_l10n_ve_auto_withholding_values(self, partner_tax):
        self.ensure_one()
        values = {'tax_id': partner_tax.tax_id.id}
        if partner_tax.tax_id.l10n_ve_tax_type == 'tabla_islr':
            partner = self.partner_id.commercial_partner_id
            regimen = partner.l10n_ve_seniat_regimen_islr_ids[:1]
            values.update({
                'calc_islr': 'all',
                'l10n_ve_regimen_islr_id': regimen.id,
            })
        return values

    @api.depends(
        "partner_id",
        "partner_id.commercial_partner_id.l10n_ve_partner_tax_ids.tax_id",
        "partner_id.commercial_partner_id.l10n_ve_partner_tax_ids.company_id",
        "partner_id.commercial_partner_id.l10n_ve_seniat_regimen_islr_ids",
        "to_pay_move_line_ids",
        "to_pay_move_line_ids.move_id.l10n_ve_withholding_ids.tax_id",
        "to_pay_move_line_ids.move_id.l10n_ve_withholding_ids.state",
        "l10n_ve_withholding_line_ids.state",
        "company_id",
        "date",
        "partner_type",
    )
    def _compute_l10n_ve_withholding_line_ids(self):
        for rec in self:
            if rec.state != "draft" and rec.l10n_ve_withholding_line_ids:
                rec.l10n_ve_withholding_islr = any(
                    line.l10n_ve_tax_type == 'tabla_islr'
                    for line in rec._get_l10n_ve_active_withholding_lines()
                )
                rec.l10n_ve_withholding_line_ids = rec.l10n_ve_withholding_line_ids
                continue
            if not rec._allow_l10n_ve_auto_withholding():
                rec.l10n_ve_withholding_islr = any(
                    line.l10n_ve_tax_type == 'tabla_islr'
                    for line in rec._get_l10n_ve_active_withholding_lines()
                )
                rec.l10n_ve_withholding_line_ids = rec.l10n_ve_withholding_line_ids
                continue
            withholdings = []
            wth_islr = False
            if rec.partner_type == "supplier":
                partner_taxes = rec._get_l10n_ve_partner_withholding_taxes()
                partner_taxes = partner_taxes.filtered(
                    lambda partner_tax: rec._has_l10n_ve_moves_without_withholding_tax(partner_tax.tax_id)
                )
                existing_tax_ids = set(
                    rec.l10n_ve_withholding_line_ids.filtered(
                        lambda withholding: withholding.state != 'cancel'
                    ).tax_id.ids
                )
                wth_islr = any(
                    tax.tax_id.l10n_ve_tax_type == 'tabla_islr'
                    for tax in partner_taxes
                )
                withholdings += [
                    Command.create(rec._prepare_l10n_ve_auto_withholding_values(tax))
                    for tax in partner_taxes
                    if tax.tax_id.id not in existing_tax_ids
                ]
            rec.l10n_ve_withholding_islr = wth_islr
            if withholdings:
                rec.l10n_ve_withholding_line_ids = withholdings
            else:
                rec.l10n_ve_withholding_line_ids = rec.l10n_ve_withholding_line_ids

    @api.depends("l10n_ve_withholding_line_ids.amount", "l10n_ve_withholding_line_ids.state")
    def _compute_l10n_ve_withholdings_amount(self):
        for payment in self:
            payment.l10n_ve_withholdings_amount = sum(
                payment._get_l10n_ve_active_withholding_lines().mapped("amount")
            )

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
                partner = payment.partner_id.commercial_partner_id
                payment.l10n_ve_partner_regimen_islr_ids = partner.l10n_ve_seniat_regimen_islr_ids
                if payment.l10n_ve_third_partner_withholding and payment.l10n_ve_third_partner_id and payment.partner_type == 'supplier':
                    third_partner = payment.l10n_ve_third_partner_id.commercial_partner_id
                    payment.l10n_ve_partner_regimen_islr_ids = third_partner.l10n_ve_seniat_regimen_islr_ids
            else:
                payment.l10n_ve_partner_regimen_islr_ids = payment.env['seniat.tabla.islr']

    @api.depends(
        'to_pay_move_line_ids.amount_residual',
        'to_pay_move_line_ids.amount_residual_currency',
        'to_pay_move_line_ids.currency_id',
        'to_pay_move_line_ids.move_id',
        'to_pay_move_line_ids.move_id.l10n_ve_withholding_ids.tax_id',
        'l10n_ve_withholding_line_ids.tax_id',
        'l10n_ve_withholding_line_ids.state',
        'date',
        'currency_id')
    def _compute_l10n_ve_withholding_taxed(self):
        for payment in self:
            withholding_taxed = 0.0
            move_line_tax_ids = []
            withholding_taxes = payment._get_l10n_ve_active_withholding_lines().filtered(
                lambda line: line.tax_id.l10n_ve_tax_type == 'partner_tax'
            ).tax_id
            company_id = payment.company_id.id if not payment.company_id.parent_id \
                else payment.company_id.parent_id.id
            tax_keys = ['tax8purchase', 'tax16purchase', 'tax31purchase', 'tax15purchase']
            tax_list = []
            for key in tax_keys:
                ref = self.env.ref(f'account.{company_id}_{key}', raise_if_not_found=False)
                if ref:
                    tax_list.append(ref.id)
            lines_to_pay = payment.to_pay_move_line_ids._origin or payment.to_pay_move_line_ids
            for line_to_pay in lines_to_pay:
                if withholding_taxes and not any(
                    payment._get_l10n_ve_moves_without_withholding_tax(tax) & line_to_pay.move_id
                    for tax in withholding_taxes
                ):
                    continue
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
        'to_pay_move_line_ids.move_id.amount_untaxed_signed',
        'to_pay_move_line_ids.move_id',
        'to_pay_move_line_ids.move_id.l10n_ve_withholding_ids.tax_id',
        'l10n_ve_withholding_line_ids.tax_id',
        'l10n_ve_withholding_line_ids.state')
    def _compute_l10n_ve_withholding_untaxed(self):
        for payment in self:
            withholding_untaxed = 0.0
            withholding_taxes = payment._get_l10n_ve_active_withholding_lines().filtered(
                lambda line: line.tax_id.l10n_ve_tax_type == 'tabla_islr'
            ).tax_id
            lines_to_pay = payment.to_pay_move_line_ids._origin or payment.to_pay_move_line_ids
            for move in lines_to_pay.mapped('move_id'):
                if withholding_taxes and not any(
                    payment._get_l10n_ve_moves_without_withholding_tax(tax) & move
                    for tax in withholding_taxes
                ):
                    continue
                withholding_untaxed += abs(move.amount_untaxed_signed)
            payment.l10n_ve_withholding_untaxed = withholding_untaxed

    @api.onchange("l10n_ve_withholdings_amount")
    def _onchange_withholdings(self):
        # con esto evitamos el importe negativo en pagos a proveedores
        for rec in self.filtered(lambda x: not x._is_latam_check_payment()):
            if rec.company_currency_id.is_zero(rec.l10n_ve_withholdings_amount):
                continue
            if rec.currency_id != rec.company_currency_id and rec.to_pay_move_line_ids:
                rec._l10n_ve_adjust_foreign_payment_for_withholdings()
                continue
            amount = rec.amount + rec.payment_difference
            rec.amount = amount if amount > 0 else 0

    def _l10n_ve_get_gross_payment_amount(self):
        self.ensure_one()
        company_currency = self.company_currency_id
        payment_currency = self.currency_id
        amount = 0.0
        for line in self.to_pay_move_line_ids._origin:
            if line.currency_id == payment_currency:
                amount += line.amount_residual_currency
            elif line.currency_id and line.currency_id != company_currency:
                amount += line.currency_id._convert(
                    line.amount_residual_currency,
                    payment_currency,
                    self.company_id,
                    self.date,
                )
            else:
                amount += company_currency._convert(
                    line.amount_residual,
                    payment_currency,
                    self.company_id,
                    self.date,
                )
        amount *= -1.0 if self.partner_type == "supplier" else 1.0
        amount += company_currency._convert(
            self.unreconciled_amount,
            payment_currency,
            self.company_id,
            self.date,
        )
        return amount

    def _l10n_ve_get_withholding_amount_in_payment_currency(self):
        self.ensure_one()
        currency_data = self._get_withholding_foreign_currency_data()
        if (
            currency_data
            and currency_data["currency"] == self.currency_id
            and currency_data["conversion_rate"]
        ):
            return self.l10n_ve_withholdings_amount / currency_data["conversion_rate"]
        return self.company_currency_id._convert(
            self.l10n_ve_withholdings_amount,
            self.currency_id,
            self.company_id,
            self.date,
            round=False,
        )

    def _l10n_ve_adjust_foreign_payment_for_withholdings(self):
        self.ensure_one()
        amount_exact = max(
            self._l10n_ve_get_gross_payment_amount()
            - self._l10n_ve_get_withholding_amount_in_payment_currency(),
            0.0,
        )
        self.amount = self.currency_id.round(amount_exact)
        if "amount_exact" in self._fields:
            self.amount_exact = amount_exact
        else:
            amount_exact = self.amount
        self.force_amount_company_currency = self.company_currency_id.round(
            self.currency_id._convert(
                amount_exact,
                self.company_currency_id,
                self.company_id,
                self.date,
                round=False,
            )
        )
        self._compute_amount_company_currency()

    @api.onchange('l10n_ve_withholding_islr')
    def _onchange_l10n_ve_withholding_islr(self):
        for payment in self:
            withholding_islr_ids = []
            if payment.l10n_ve_withholding_islr:
                to_pay = payment.to_pay_move_line_ids[:1]
                if not to_pay:
                    payment.l10n_ve_withholding_line_ids = payment._delete_islr_lines()
                    continue
                tax_id = self.env['account.tax'].search([
                    ('l10n_ve_withholding_payment_type', '=', 'supplier'),
                    ('l10n_ve_tax_type', '=', 'tabla_islr')
                ], limit=1)
                if to_pay.move_id and tax_id and payment._has_l10n_ve_moves_without_withholding_tax(tax_id):
                    withholding_islr_ids.append(Command.create({
                        'tax_id': tax_id.id,
                        'payment_id': payment.id,
                        'calc_islr': 'all'
                    }))
            else:
                withholding_islr_ids = payment._delete_islr_lines()
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
                withholding_islr_ids = payment._delete_islr_lines()
                to_pay = payment.to_pay_move_line_ids[:1]
                if not to_pay:
                    payment.l10n_ve_withholding_line_ids = withholding_islr_ids
                    continue
                tax_id = self.env['account.tax'].search([
                    ('l10n_ve_withholding_payment_type', '=', 'supplier'),
                    ('l10n_ve_tax_type', '=', 'tabla_islr')
                ], limit=1)
                if to_pay.move_id.invoice_line_ids and tax_id and payment._has_l10n_ve_moves_without_withholding_tax(tax_id):
                    for line in to_pay.move_id.invoice_line_ids:
                        if not line.product_id.product_tmpl_id.l10n_ve_disable_islr:
                            withholding_islr_ids.append(Command.create({
                                'tax_id': tax_id.id,
                                'payment_id': payment.id,
                                'move_line_id': line.id,
                                'calc_islr': 'line'
                            }))
            else:
                withholding_islr_ids = payment._delete_islr_lines()
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

    def _needs_withholding_draft_bypass(self):
        """Detect payments likely to hit unbalanced-move on reset-to-draft."""
        self.ensure_one()

        if not self._get_l10n_ve_active_withholding_lines():
            return False
        if not self.move_id or self.move_id.state not in ("posted", "cancel"):
            return False

        payment_move_lines = self.move_id.line_ids.filtered(lambda line: line.payment_id == self)
        if not payment_move_lines:
            payment_move_lines = self.move_id.line_ids
        tax_payment_lines = payment_move_lines.filtered("tax_line_id")
        if not tax_payment_lines:
            return False
        return True

    def action_draft(self):
        if self.env.context.get("skip_withholding_draft_guard"):
            return super(AccountPayment, self).action_draft()

        risky_payments = self.filtered(lambda p: p._needs_withholding_draft_bypass())
        safe_payments = self - risky_payments

        if safe_payments:
            super(AccountPayment, safe_payments).action_draft()

        if risky_payments:
            super(
                AccountPayment,
                risky_payments.with_context(
                    check_move_validity=False,
                    skip_withholding_draft_guard=True,
                ),
            ).action_draft()

        return True

    def _get_l10n_ve_numbered_withholding_lines(self):
        return self.l10n_ve_withholding_line_ids.filtered(
            lambda withholding: withholding._has_control_number()
        )

    def _write_l10n_ve_numbered_withholding_snapshot(self, state=False, cancel=False, detach=False):
        for payment in self:
            payment._get_l10n_ve_numbered_withholding_lines()._write_payment_snapshot(
                state=state,
                cancel=cancel,
                detach=detach,
            )

    def _l10n_ve_find_withholding_move_line(self, withholding):
        """Locate the payment move line that corresponds to a withholding."""
        self.ensure_one()
        move = self.move_id
        if not move:
            return self.env["account.move.line"]

        linked = move.line_ids.filtered(
            lambda aml: aml.l10n_ve_withholding_line_id == withholding
        )
        if linked:
            return linked[:1]

        __, account_id, __, __ = withholding._tax_compute_all_helper()
        company_currency = self.company_id.currency_id
        amount = company_currency.round(withholding.amount)
        candidates = move.line_ids.filtered(
            lambda aml: aml.account_id.id == account_id
            and company_currency.compare_amounts(
                company_currency.round(abs(aml.balance)),
                amount,
            ) == 0
        )
        if len(candidates) == 1:
            return candidates
        named = candidates.filtered(lambda aml: aml.name == withholding.name)
        if named:
            return named[:1]
        empty = candidates.filtered(lambda aml: not aml.name)
        if empty:
            return empty[:1]
        return candidates[:1]

    def _l10n_ve_sync_withholding_names_to_move(self, tax_types=None):
        """Ensure withholding control numbers are visible in the general ledger.

        Writes ``account.move.line.name`` (Communication) even when the move is
        already posted, because ``_synchronize_to_moves`` skips posted moves.

        :param tax_types: optional iterable of ``account.tax.l10n_ve_tax_type``
            values to sync (e.g. ``('tabla_islr',)``). ``None`` syncs all.
        """
        MoveLine = self.env["account.move.line"].with_context(
            check_move_validity=False,
            skip_invoice_sync=True,
        )
        tax_types = set(tax_types) if tax_types else None
        for payment in self:
            if not payment.move_id:
                continue
            withholdings = payment._get_l10n_ve_active_withholding_lines()
            if tax_types is not None:
                withholdings = withholdings.filtered(
                    lambda w: w.tax_id.l10n_ve_tax_type in tax_types
                )
            for withholding in withholdings:
                if not withholding._has_control_number():
                    continue
                aml = payment._l10n_ve_find_withholding_move_line(withholding)
                if not aml:
                    _logger.warning(
                        "Payment %s: no move line found for withholding %s (%s)",
                        payment.name,
                        withholding.id,
                        withholding.name,
                    )
                    continue
                __, __, tax_repartition_line_id, __ = withholding._tax_compute_all_helper()
                vals = {}
                if aml.name != withholding.name:
                    vals["name"] = withholding.name
                if aml.tax_repartition_line_id.id != tax_repartition_line_id:
                    vals["tax_repartition_line_id"] = tax_repartition_line_id
                if aml.l10n_ve_withholding_line_id != withholding:
                    vals["l10n_ve_withholding_line_id"] = withholding.id
                if vals:
                    MoveLine.browse(aml.id).write(vals)

    def action_post(self):
        for payment in self:
            if payment.to_pay_move_line_ids:
                to_pay_moves = payment.to_pay_move_line_ids.mapped('move_id')
                first_move = to_pay_moves[:1]
                if first_move.move_type == 'in_refund' and payment.l10n_ve_withholdings_amount:
                    payment.write({
                        'payment_type': 'inbound',
                    })
            commands = []
            for line in payment._get_l10n_ve_active_withholding_lines() if payment.partner_type == 'supplier' else []:
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
        for payment in self:
            payment._l10n_ve_sync_withholding_names_to_move()
            payment._write_l10n_ve_numbered_withholding_snapshot(state='posted')
            if not payment.to_pay_move_line_ids:
                continue
            for move in payment.to_pay_move_line_ids.mapped('move_id'):
                # Link withholdings after posting so the computed draft suggestions
                # do not wipe the lines that were just confirmed on this payment.
                wth_to_add = [
                    wth.id for wth in payment._get_l10n_ve_active_withholding_lines()
                    if not payment._move_has_l10n_ve_withholding_tax(move, wth.tax_id)
                ]
                current_ids = move.l10n_ve_withholding_ids.ids
                all_ids = list(set(current_ids + wth_to_add))
                move.l10n_ve_withholding_ids = [Command.set(all_ids)]

                # Relacionamos los pagos a la factura (User Ux)
                # TODO: Revisar si esto es correcto y funcional
                move.write({"matched_payment_ids": [Command.link(payment.id)]})
        # if self.l10n_ve_withholding_line_ids and self.matched_move_line_ids and self.payment_type == 'outbound':
        #     invoice_id = self.mapped('matched_move_line_ids.move_id').filtered(lambda m: m.move_type == 'in_invoice')
        #     if self.date != invoice_id.invoice_date:
        #         raise UserError(
        #             _("Error de Retenciones\n\n"
        #               "Lo sentimos, no es posible registrar un pago de retención con una fecha distinta a la de la factura asociada (**%s**).\n\n"
        #               "**Alternativa de Solución:**\n"
        #               "Puede registrar la transacción en dos partes:\n"
        #               "1. Un pago por el monto exacto de la retención, utilizando la **fecha de la factura**.\n"
        #               "2. Un segundo pago por el resto del monto (si aplica), utilizando la **fecha deseada**.")
        #               % invoice_id.invoice_date.strftime('%Y-%m-%d')
        #         )
        return res

    def action_cancel(self):
        res = super(AccountPayment, self).action_cancel()
        self._write_l10n_ve_numbered_withholding_snapshot(state='cancel', cancel=True)
        return res

    def unlink(self):
        for payment in self:
            numbered_withholdings = payment._get_l10n_ve_numbered_withholding_lines()
            draft_withholdings = payment.l10n_ve_withholding_line_ids - numbered_withholdings
            if draft_withholdings:
                draft_withholdings.unlink()
            if numbered_withholdings:
                numbered_withholdings._write_payment_snapshot(
                    state='cancel',
                    cancel=True,
                    detach=True,
                )
        return super(AccountPayment, self).unlink()

    def _prepare_move_lines_per_type(self, write_off_line_vals=None, force_balance=None):
        res = super()._prepare_move_lines_per_type(write_off_line_vals=write_off_line_vals, force_balance=force_balance)
        wth_lines = res.get("withholding_lines", [])
        if wth_lines:
            wth_balance = sum(line["balance"] for line in wth_lines)
            wth_amount_currency = sum(line["amount_currency"] for line in wth_lines)
            wth_currency_ids = {line.get("currency_id") for line in wth_lines if line.get("currency_id")}
            wth_currency_id = next(iter(wth_currency_ids), False) if len(wth_currency_ids) == 1 else False

            def _same_currency_for_amount_currency(line_vals):
                line_currency_id = line_vals.get("currency_id")
                if line_currency_id:
                    return bool(wth_currency_id and line_currency_id == wth_currency_id)
                # lines without currency_id are company-currency lines
                return bool(wth_currency_id and wth_currency_id == self.company_currency_id.id)

            liquidity_lines = res.get("liquidity_lines", [])
            if liquidity_lines:
                liquidity_lines[0]["balance"] += wth_balance
                if _same_currency_for_amount_currency(liquidity_lines[0]):
                    liquidity_lines[0]["amount_currency"] += wth_amount_currency
                elif wth_currency_id:
                    # Super already subtracts withholding_amount_currency from liquidity amount_currency.
                    # If currencies differ, undo that subtraction to avoid cross-currency corruption.
                    liquidity_lines[0]["amount_currency"] += wth_amount_currency
                if self.company_currency_id.is_zero(liquidity_lines[0]["balance"]):
                    res["liquidity_lines"] = []

            counterpart_lines = res.get("counterpart_lines", [])
            if counterpart_lines:
                # the counterpart line (debt) should be the gross amount (net + withholdings)
                counterpart_lines[0]["balance"] -= wth_balance
                if _same_currency_for_amount_currency(counterpart_lines[0]):
                    counterpart_lines[0]["amount_currency"] -= wth_amount_currency

            # If we are generating a withholding-only payment (liquidity line dropped) against
            # foreign debt currency, force the counterpart line to that foreign currency.
            if not res.get("liquidity_lines") and counterpart_lines and wth_currency_id and wth_currency_id != self.company_currency_id.id:
                counterpart_lines[0]["currency_id"] = wth_currency_id
                counterpart_lines[0]["amount_currency"] = -wth_amount_currency

            # Keep amount_currency coherent on company-currency lines.
            for line_vals in (res.get("liquidity_lines", []) + counterpart_lines):
                line_currency_id = line_vals.get("currency_id")
                if not line_currency_id or line_currency_id == self.company_currency_id.id:
                    line_vals["amount_currency"] = line_vals["balance"]

        return res

    def _get_withholding_foreign_currency_data(self):
        """Detect foreign debt currency and conversion rate from invoice rate.

        This is used to keep debit/credit in company currency while setting
        amount_currency/currency_id in invoice foreign currency (e.g. USD).
        """
        self.ensure_one()
        company_currency = self.company_id.currency_id
        debt_lines = self.to_pay_move_line_ids._origin
        if not debt_lines:
            return None

        foreign_lines = debt_lines.filtered(
            lambda l: l.currency_id
            and l.currency_id != company_currency
            and not l.currency_id.is_zero(l.amount_residual_currency)
        )
        foreign_currencies = foreign_lines.mapped("currency_id")
        if len(foreign_currencies) != 1:
            return None

        total_foreign = sum(abs(line.amount_residual_currency) for line in foreign_lines)
        if foreign_currencies.is_zero(total_foreign):
            return None

        # Main rule: withholding amount_currency = withholding amount / invoice rate.
        weighted_rate_sum = 0.0
        for line in foreign_lines:
            move = line.move_id
            invoice_rate = getattr(move, "inverse_invoice_currency_rate", 0.0) or 0.0
            if invoice_rate:
                weighted_rate_sum += abs(line.amount_residual_currency) * invoice_rate

        conversion_rate = 0.0
        if weighted_rate_sum:
            conversion_rate = weighted_rate_sum / total_foreign
        else:
            # Fallback: implied rate from current residual amounts.
            total_company = sum(abs(line.amount_residual) for line in foreign_lines)
            if company_currency.is_zero(total_company):
                return None
            conversion_rate = total_company / total_foreign

        return {
            "currency": foreign_currencies,
            "conversion_rate": conversion_rate,
        }

    def _prepare_move_withholding_lines(self, default_values):
        res = super()._prepare_move_withholding_lines(default_values)
        self.ensure_one()
        sign = 1
        if self.payment_type == "outbound":
            sign = -1

        currency_data = self._get_withholding_foreign_currency_data()
        move_currency = currency_data["currency"] if currency_data else self.currency_id
        conversion_rate = (
            currency_data["conversion_rate"]
            if currency_data else (self.exchange_rate or 1.0)
        )
        active_withholding_lines = self._get_l10n_ve_active_withholding_lines()
        for line in active_withholding_lines:
            __, account_id, tax_repartition_line_id, __ = line._tax_compute_all_helper()
            balance = self.company_id.currency_id.round(sign * line.amount)
            amount_currency = move_currency.round(balance / conversion_rate)
            res.append(
                {
                    **self._get_withholding_move_line_default_values(),
                    "name": line.name,
                    "l10n_ve_withholding_line_id": line.id,
                    "account_id": account_id,
                    "balance": balance,
                    "amount_currency": amount_currency,
                    "currency_id": move_currency.id,
                    "tax_base_amount": sign * line.base_amount,
                    "tax_repartition_line_id": tax_repartition_line_id,
                }
            )
        account_id = self.company_id.l10n_ve_tax_base_account_id.id
        if account_id:
            for base_amount in list(set(active_withholding_lines.mapped("base_amount"))):
                withholding_lines = active_withholding_lines.filtered(lambda x: x.base_amount == base_amount)
                nice_base_label = ",".join(withholding_lines.filtered("name").mapped("name"))
                account_id = self.company_id.l10n_ve_tax_base_account_id.id
                balance = self.company_id.currency_id.round(sign * base_amount)
                # informamos el amount_currency para que Odoo no resetee el balance a 0.0 por inconsistencia de moneda
                amount_currency = move_currency.round(balance / conversion_rate)
                res.append(
                    {
                        **self._get_withholding_move_line_default_values(),
                        "name": _("Base Ret: ") + nice_base_label,
                        "tax_ids": [Command.set(withholding_lines.mapped("tax_id").ids)],
                        "account_id": account_id,
                        "balance": balance,
                        "amount_currency": amount_currency,
                        "currency_id": move_currency.id,
                    }
                )
                res.append(
                    {
                        **self._get_withholding_move_line_default_values(),  # Counterpart 0 operation
                        "name": _("Base Ret Cont: ") + nice_base_label,
                        "account_id": account_id,
                        "balance": -balance,
                        "amount_currency": -amount_currency,
                        "currency_id": move_currency.id,
                    }
                )

        return res

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
