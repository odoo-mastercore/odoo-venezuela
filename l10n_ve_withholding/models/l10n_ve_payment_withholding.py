# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError


class l10nVePaymentWithholding(models.Model):
    _name = "l10n_ve.payment.withholding"
    _description = "Payment withholding lines"

    payment_id = fields.Many2one("account.payment", required=True, ondelete="cascade")
    partner_id = fields.Many2one(related="payment_id.partner_id")
    company_id = fields.Many2one(related="payment_id.company_id")
    currency_id = fields.Many2one(related="payment_id.company_currency_id")
    l10n_ve_tax_type = fields.Selection(related="tax_id.l10n_ve_tax_type")
    name = fields.Char(string="Number")
    ref = fields.Text(compute="_compute_amount", store=True, readonly=False, string="Ref")
    tax_id = fields.Many2one("account.tax", check_company=True, required=True, string="Tax")
    withholding_sequence_id = fields.Many2one(related="tax_id.l10n_ve_withholding_sequence_id")
    base_amount = fields.Monetary(compute="_compute_base_amount", store=True, readonly=False, string="Base Amount")
    amount = fields.Monetary(compute="_compute_amount", store=True, readonly=False, string="Amount")
    l10n_ve_move_line_taxes_ids = fields.Many2many(related="payment_id.l10n_ve_move_line_taxes_ids")
    # ISLR
    l10n_ve_concept_withholding = fields.Char(string='Concept withholding')
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Linea de factura'
    )
    calc_islr = fields.Selection(
        string='Cálculo de ISLR',
        selection=[
            ('all', 'Global'),
            ('line', 'line')
        ]
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        related='move_line_id.product_id',
    )
    l10n_ve_regimen_islr_id = fields.Many2one(
        'seniat.tabla.islr',
        'Aplicativo ISLR'
    )
    date = fields.Date(
        string=_('Fecha'),
        related='payment_id.date',
        store=True,
    )

    @api.depends(
        "tax_id",
        "payment_id.l10n_ve_withholding_taxed",
        "payment_id.l10n_ve_withholding_untaxed",
        "payment_id.l10n_ve_withholdable_advanced_amount",
        "payment_id.unreconciled_amount",
    )
    def _compute_base_amount(self):
        self.payment_id._compute_to_pay_amount()
        for wth in self.filtered(lambda x: x.payment_id.partner_type == "supplier"):
            advance_amount = wth.payment_id.l10n_ve_withholdable_advanced_amount
            tax = wth._get_withholding_tax()
            if tax and not tax.l10n_ve_tax_type in ["tabla_islr", "partner_tax"]:
                raise UserError(_(
                        "El impuesto %s no pertenece a ningún tipo de retención. Por favor, verifique el impuesto seleccionado."
                    ) % (
                        tax.name,
                    )
                )
            if advance_amount < 0.0 and wth.payment_id.to_pay_move_line_ids:
                sorted_to_pay_lines = sorted(
                    wth.payment_id.to_pay_move_line_ids, key=lambda a: a.date_maturity or a.date
                )
                partial_line = sorted_to_pay_lines[-1]
                if -partial_line.amount_residual < -wth.payment_id.l10n_ve_withholdable_advanced_amount:
                    raise UserError(
                        _(
                            "Seleccionó deuda por %s pero aparentente desea pagar %s. En la deuda seleccionada hay algunos comprobantes de mas que no van a poder ser pagados (%s). Deberá quitar dichos comprobantes de la deuda seleccionada para poder hacer el correcto cálculo de las retenciones."
                        )
                        % (
                            wth.payment_id.selected_debt,
                            wth.payment_id.to_pay_amount,
                            partial_line.move_id.display_name,
                        )
                    )
                advance_amount = wth.payment_id.unreconciled_amount

            # Verificar calculo por retencion de iva o islr
            if tax.l10n_ve_tax_type == "partner_tax":
                wth.base_amount = wth.payment_id.l10n_ve_withholding_taxed + advance_amount
            else:
                if wth.calc_islr == 'all':
                    wth.base_amount = wth.payment_id.l10n_ve_withholding_untaxed + advance_amount
                elif wth.calc_islr == 'line' and wth.move_line_id:
                    wth.base_amount = abs(wth.move_line_id.price_subtotal) + advance_amount

    @api.depends("base_amount", "tax_id", "l10n_ve_regimen_islr_id")
    def _compute_amount(self):
        for line in self.filtered(lambda r: r.payment_id.partner_type == "supplier"):
            tax_id = line._get_withholding_tax()
            if not tax_id:
                line.amount = 0.0
                line.ref = False
            else:
                tax_amount, __, __, ref = line._tax_compute_all_helper()
                line.amount = tax_amount
                line.ref = ref

    def _tax_compute_all_helper(self):
        """practicamente mismo codigo que en l10n_ar.payment.register.withholding"""
        self.ensure_one()
        tax = self._get_withholding_tax()
        if not tax.amount_type:
            raise UserError(
                _(
                    "El impuesto de retención %s no tiene un tipo de cálculo definido. Por favor, defina el tipo de cálculo en la configuración del impuesto."
                )
                % tax.name
            )
        amount = 0.0
        if self.tax_id.l10n_ve_tax_type == 'partner_tax' and self.payment_id.partner_type == 'supplier':
            alicuota_retencion = self._get_partner_alicuot(self.payment_id.partner_id)
            alicuota = int(alicuota_retencion) / 100.0
            base_amount = self.base_amount
            amount = base_amount * (alicuota)
        elif self.tax_id.l10n_ve_tax_type == 'tabla_islr' and self.payment_id.partner_type == 'supplier':
            regimen_id = self.l10n_ve_regimen_islr_id or False
            if regimen_id:
                base = self.base_amount
                base_withholding = base * (
                    regimen_id.withholding_base_percentage / 100)
                withholding_percentage = 0.0
                base_ut = 0.0
                subtracting = 0.0
                withholding = 0.0
                for band in regimen_id.banda_calculo_ids:
                    if band.type_amount == 'ut':
                        base_ut = base / regimen_id.seniat_ut_id.amount
                    else:
                        base_ut = base
                    if base_ut >= band.amount_minimum and base_ut <= band.amount_maximum:
                        withholding_percentage = band.withholding_percentage / 100

                    elif base_ut > band.amount_minimum and band.amount_maximum == 0.0:
                        withholding_percentage = band.withholding_percentage / 100
                    if regimen_id.type_subtracting == 'amount' and \
                        band.type_amount == 'ut':
                        subtracting = band.withholding_amount * \
                        regimen_id.seniat_ut_id.amount

                    elif regimen_id.type_subtracting == 'amount' and \
                        band.type_amount == 'bs':
                        subtracting = band.withholding_amount

                if subtracting > 0.0:
                    withholding = (base_withholding *
                                withholding_percentage) - subtracting
                else:
                    withholding = base_withholding * withholding_percentage
                # TODO: Pasar a ext
                # if currency.id != self.company_id.currency_id.id:
                #     date = self.payment_id.payment_date
                #     currency_rate = self.env['res.currency.rate'].search([
                #                     ('currency_id.id','=',currency.id),
                #                     ('name', '<=', date)],limit=1).inverse_company_rate
                #     amount = withholding / (currency_rate or 1)
                # else:
                amount = withholding

        taxes_res = tax.compute_all(
            amount,
            currency=self.payment_id.currency_id,
            quantity=1.0,
            product=False,
            partner=False,
            is_refund=False,
        )
        tax_amount = amount
        tax_account_id = taxes_res["taxes"][0]["account_id"]
        tax_repartition_line_id = taxes_res["taxes"][0]["tax_repartition_line_id"]

        ref = False
        if self.payment_id.partner_type == 'supplier':
            if tax.l10n_ve_tax_type == 'partner_tax':
                ref = f"({self.base_amount} * {alicuota_retencion}%)"
            #TODO: Aplicar ref para islr

        return tax_amount, tax_account_id, tax_repartition_line_id, ref

    def _get_partner_alicuot(self, partner):
        self.ensure_one()
        if partner.l10n_ve_vat_retention:
            alicuot = partner.l10n_ve_vat_retention
        else:
            raise UserError(_(
                'Si utiliza Cálculo de impuestos igual a "Alícuota en el '
                'Partner", debe setear el campo de retención de IVA'
                ' en la ficha del partner, seccion Contabilidad'))
        return alicuot

    def _get_same_period_dates(self):
        self.ensure_one()
        to_date = self.payment_id.date or datetime.date.today()
        from_date = to_date + relativedelta(day=1)
        return to_date, from_date

    def _get_same_period_withholdings_domain(self):
        """Returns a heritable domain of earnings withholdings that
        belong to the same regime, same commercial partner,
        and from the month of payment between the 1st and the day of payment.
        """
        self.ensure_one()
        to_date, from_date = self._get_same_period_dates()
        tax_id = self._get_withholding_tax()
        return [
            *self.env["account.move.line"]._check_company_domain(tax_id.company_id),
            ("parent_state", "=", "posted"),
            ("tax_line_id.l10n_ve_tax_type", "in", ["tabla_islr", "partner_tax"]),
            ("partner_id", "=", self.payment_id.partner_id.commercial_partner_id.id),
            ("date", "<=", to_date),
            ("date", ">=", from_date),
        ]

    def _get_same_period_withholdings_amount(self):
        """Return Cummulated withholding amount"""
        self.ensure_one()
        # We search for the payments in the same month of the same regimen and the same code.
        domain_same_period_withholdings = self._get_same_period_withholdings_domain()
        if same_period_partner_withholdings := self.env["account.move.line"]._read_group(
            domain_same_period_withholdings, ["partner_id"], ["balance:sum"]
        ):
            return abs(same_period_partner_withholdings[0][1])
        return 0.0

    def _get_same_period_base_domain(self):
        """Returns a heritable domain of earnings bases that
        belong to the same regime, same commercial partner,
        and from the month of payment between the 1st and the day of payment.
        """
        self.ensure_one()
        to_date, from_date = self._get_same_period_dates()
        tax_id = self._get_withholding_tax()
        return [
            *self.env["account.move.line"]._check_company_domain(tax_id.company_id),
            ("parent_state", "=", "posted"),
            ("tax_line_id.l10n_ve_tax_type", "in", ["tabla_islr", "partner_tax"]),
            ("partner_id", "=", self.payment_id.partner_id.commercial_partner_id.id),
            ("date", "<=", to_date),
            ("date", ">=", from_date),
        ]

    def _get_same_period_base_amount(self):
        """Return Cummulated withholding base"""
        self.ensure_one()
        domain_same_period_base = self._get_same_period_base_domain()
        if same_period_partner_base := self.env["account.move.line"]._read_group(
            domain_same_period_base, ["partner_id"], ["balance:sum"]
        ):
            return abs(same_period_partner_base[0][1])
        return 0.0

    def _get_withholding_tax(self):
        """Return the applicable withheld tax"""
        self.ensure_one()
        return self.tax_id

    def _get_withholding_lines(self):
        lines = []
        if self.l10n_ve_move_line_taxes_ids:
            for idx, tax in enumerate(self.l10n_ve_move_line_taxes_ids, start=1):
                lines.append({
                    'index': idx,
                    'date': tax.move_id.invoice_date.strftime('%d-%m-%Y'),
                    'move_ref': tax.move_id.ref or '',
                    'l10n_ve_control_number': tax.move_id.l10n_ve_control_number,
                    'move_type': tax.move_id.move_type or '',
                    'move_id': True if tax.move_id else False,
                    'reserved_entry': True if tax.move_id.reversed_entry_id else False,
                    'reserved_entry_ref': tax.move_id.reversed_entry_id.ref or '',
                    'amount_total': self.payment_id._format_miles_number(round(abs(tax.move_id.amount_total_signed), 2)),
                    'amount_untaxed': self.payment_id._format_miles_number(tax.move_id.get_exempt_amount()),
                    'tax_base_amount': self.payment_id._format_miles_number(tax.tax_base_amount),
                    'tax_name': tax.tax_line_id.name,
                    'partner_vat_retention': str(self._get_partner_alicuot(self.payment_id.partner_id)),
                    'tax_debit': self.payment_id._format_miles_number(tax.debit) if tax.move_id.move_type == 'in_invoice' else self.payment_id._format_miles_number(tax.credit),
                    'tax_amount': self.payment_id._format_miles_number(tax.debit * int(self._get_partner_alicuot(self.payment_id.partner_id)) / 100) if tax.debit else self.payment_id._format_miles_number(tax.credit * int(self._get_partner_alicuot(self.payment_id.partner_id)) / 100),
                })
        return lines

    def _get_sustraendo(self):
        if self.l10n_ve_regimen_islr_id:
            regimen_id = self.l10n_ve_regimen_islr_id
            if regimen_id and regimen_id.type_subtracting == 'amount':
                return self._format_miles_number(
                    regimen_id.banda_calculo_ids[0].withholding_amount
                )
        return False

    def _format_miles_number(self, number):
        return '{:,.2f}'.format(number).replace(",", "@").replace(".", ",").replace("@", ".")

    ##########
    # ACTIONS
    ##########

    # def action_l10n_ve_payment_withholding_tree(self):
    #     """Open a tree view showing previous withholdings."""
    #     same_period_withholdings = (
    #         self.env["account.move.line"].search(self._get_same_period_withholdings_domain()).withholding_id
    #     )
    #     return {
    #         "name": "Previous Withholdings",
    #         "type": "ir.actions.act_window",
    #         "res_model": "l10n_ve.payment.withholding",
    #         "view_mode": "list",
    #         "view_id": self.env.ref("l10n_ve_tax.view_l10n_ve_payment_withholding_tree").id,
    #         "domain": [("id", "in", same_period_withholdings.ids)],
    #     }
