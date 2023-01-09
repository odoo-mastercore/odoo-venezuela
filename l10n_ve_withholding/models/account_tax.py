from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from odoo.tools.safe_eval import safe_eval
from dateutil.relativedelta import relativedelta
import datetime

import logging

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    amount_type = fields.Selection(
        selection_add=([
            ('partner_tax', 'Alícuota en el Partner'),
        ]), ondelete={'partner_tax': 'set default'}
    )
    withholding_type = fields.Selection(
        selection_add=([
            ('tabla_islr', 'Tabla ISLR'),
            ('partner_tax', 'Alícuota en el Partner'),
        ]), ondelete={'tabla_islr': 'set default', 'partner_tax': 'set default'}
    )

    def get_withholding_vals(self, payment_group):
        commercial_partner = payment_group.commercial_partner_id

        force_withholding_amount_type = None
        if self.withholding_type == 'partner_tax' and payment_group.iva == True:
            alicuota_retencion = self.get_partner_alicuot(commercial_partner)
            alicuota = int(alicuota_retencion) / 100.0
            force_withholding_amount_type = self.withholding_amount_type

            vals = super(AccountTax, self).get_withholding_vals(
                payment_group, force_withholding_amount_type)
            base_amount = payment_group.selected_debt_taxed
            base_invoice = [
                x.balance * -1.0 for x in payment_group.to_pay_move_line_ids][0]
            amount = base_amount * (alicuota)
            vals['comment_withholding'] = "%s x %s" % (
                base_amount, alicuota)
            vals['total_amount'] = base_invoice
            to_pay = payment_group.to_pay_move_line_ids[0]
            selected_debt_untaxed = 0.00
            if to_pay:
                selected_debt_taxed = 0.0
                if to_pay.currency_id.id != payment_group.company_id.currency_id.id:
                    for li in to_pay.move_id.line_ids:
                        if li.name == 'IVA (16.0%) compras':
                            selected_debt_taxed += li.amount_currency
                        elif li.name == 'IVA (8.0%) compras':
                            selected_debt_taxed += li.amount_currency
                    currency_tax = selected_debt_taxed*alicuota
                    vals['amount'] = currency_tax
                    vals['currency_id'] = to_pay.currency_id.id
                    vals['amount_company_currency'] = amount
                if to_pay.move_id.line_ids:
                    for abg in to_pay.move_id.line_ids:
                        if abg.tax_ids:
                            if abg.tax_ids[0].amount == 16.00:
                                selected_debt_untaxed += abg.debit
                                if abg.credit:
                                    selected_debt_untaxed += (
                                        abg.credit * -1.00)
                            elif abg.tax_ids[0].amount == 8.00:
                                selected_debt_untaxed += abg.debit
                                if abg.credit:
                                    selected_debt_untaxed += (
                                        abg.credit * -1.00)
            vals['withholdable_invoiced_amount'] = selected_debt_untaxed
            vals['withholdable_base_amount'] = base_amount
            vals['period_withholding_amount'] = amount

        elif self.withholding_type == 'tabla_islr':
            regimen = payment_group.regimen_islr_id
            vals = super(AccountTax, self).get_withholding_vals(
                payment_group, force_withholding_amount_type)

            to_pay = payment_group.to_pay_move_line_ids[0]
            base = (
                to_pay.move_id.amount_untaxed_signed * -1.00)
            base_withholding = base * (
                regimen.withholding_base_percentage / 100)
            withholding_percentage = 0.0
            base_ut = 0.0
            subtracting = 0.0
            withholding = 0.0
            for band in regimen.banda_calculo_ids:
                if band.type_amount == 'ut':
                    base_ut = base / regimen.seniat_ut_id.amount
                else:
                    base_ut = base
                if base_ut >= band.amount_minimum and base_ut <= band.amount_maximum:
                    withholding_percentage = band.withholding_percentage / 100

                elif base_ut > band.amount_minimum and band.amount_maximum == 0.0:
                    withholding_percentage = band.withholding_percentage / 100
                if regimen.type_subtracting == 'amount' and \
                    band.type_amount == 'ut':
                    subtracting = band.withholding_amount * \
                    regimen.seniat_ut_id.amount

                elif regimen.type_subtracting == 'amount' and \
                    band.type_amount == 'bs':
                    subtracting = band.withholding_amount

            if subtracting > 0.0:
                withholding = (base_withholding *
                               withholding_percentage) - subtracting
            else:
                withholding = base_withholding * withholding_percentage

            vals['comment_withholding'] = str(withholding_percentage*100)+"%"
            vals['total_amount'] = base
            vals['withholdable_invoiced_amount'] = base
            vals['withholdable_base_amount'] = base_withholding
            vals['period_withholding_amount'] = withholding

        else:
            vals = super(AccountTax, self).get_withholding_vals(
                payment_group, force_withholding_amount_type)
        return vals

    def get_partner_alicuota_percepcion(self, partner, date):
        if partner and date:
            arba = self.get_partner_alicuot(partner)
            return arba.alicuota_percepcion / 100.0
        return 0.0

    def get_partner_alicuot(self, partner):
        self.ensure_one()
        if partner.vat_retention:
            alicuot = partner.vat_retention
        else:
            raise UserError(_(
                'Si utiliza Cálculo de impuestos igual a "Alícuota en el '
                'Partner", debe setear el campo de retención de IVA'
                ' en la ficha del partner, seccion Compra'))

        return alicuot

    #TODO:Ubicar una mejor forma de hacer el inherit
    def create_payment_withholdings(self, payment_group):
        for tax in self.filtered(lambda x: x.withholding_type != 'none'):
            payment_withholding = self.env[
                'account.payment'].search([
                    ('payment_group_id', '=', payment_group.id),
                    ('tax_withholding_id', '=', tax.id),
                    ('automatic', '=', True),
                ], limit=1)
            if (
                    tax.withholding_user_error_message and
                    tax.withholding_user_error_domain):
                try:
                    domain = literal_eval(tax.withholding_user_error_domain)
                except Exception as e:
                    raise ValidationError(_(
                        'Could not eval rule domain "%s".\n'
                        'This is what we get:\n%s' % (
                            tax.withholding_user_error_domain, e)))
                domain.append(('id', '=', payment_group.id))
                if payment_group.search(domain):
                    raise ValidationError(tax.withholding_user_error_message)
            vals = tax.get_withholding_vals(payment_group)

            # we set computed_withholding_amount, hacemos round porque
            # si no puede pasarse un valor con mas decimales del que se ve
            # y terminar dando error en el asiento por debitos y creditos no
            # son iguales, algo parecido hace odoo en el compute_all de taxes
            currency = payment_group.currency_id
            period_withholding_amount = currency.round(vals.get(
                'period_withholding_amount', 0.0))
            previous_withholding_amount = currency.round(vals.get(
                'previous_withholding_amount'))
            # withholding can not be negative
            computed_withholding_amount = max(0, (
                period_withholding_amount - previous_withholding_amount))

            if not computed_withholding_amount:
                # if on refresh no more withholding, we delete if it exists
                if payment_withholding:
                    payment_withholding.unlink()
                continue

            # we copy withholdable_base_amount on base_amount
            # al final vimos con varios clientes que este monto base
            # debe ser la base imponible de lo que se está pagando en este
            # voucher
            vals['withholding_base_amount'] = vals.get(
                'withholdable_advanced_amount') + vals.get(
                'withholdable_invoiced_amount')
            if vals.get('currency_id') == payment_group.company_id.currency_id.id:
                vals['amount'] = computed_withholding_amount
            vals['computed_withholding_amount'] = computed_withholding_amount

            # por ahora no imprimimos el comment, podemos ver de llevarlo a
            # otro campo si es de utilidad
            vals.pop('comment')
            if payment_withholding:
                payment_withholding.write(vals)
            else:
                payment_method = self.env.ref(
                    'account_withholding.'
                    'account_payment_method_out_withholding')
                if payment_group.iva:
                    journal = self.env['account.journal'].search([
                        ('company_id', '=', tax.company_id.id),
                        ('outbound_payment_method_line_ids.payment_method_id',
                         '=', payment_method.id),
                        ('type', 'in', ['cash', 'bank']),
                        ('apply_iva', '=', True),
                    ], limit=1)
                if payment_group.islr:
                    journal = self.env['account.journal'].search([
                        ('company_id', '=', tax.company_id.id),
                        ('outbound_payment_method_line_ids.payment_method_id','=', payment_method.id),
                        ('type', 'in', ['cash', 'bank']),
                        ('apply_islr', '=', True),
                    ], limit=1)
                if not journal:
                    raise UserError(_(
                        'No journal for withholdings found on company %s') % (
                        tax.company_id.name))

                method = journal._get_available_payment_method_lines('outbound').filtered(
                    lambda x: x.code == 'withholding')

                vals['journal_id'] = journal.id
                vals['payment_method_line_id'] = method.id
                vals['payment_type'] = 'outbound'
                vals['partner_type'] = payment_group.partner_type
                vals['partner_id'] = payment_group.partner_id.id
                payment_withholding = payment_withholding.create(vals)
        return True
