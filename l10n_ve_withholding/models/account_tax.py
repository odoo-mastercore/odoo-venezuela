from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    amount_type = fields.Selection(
        selection_add=([
            ('partner_tax', 'Alícuota en el Partner'),
        ])
    )
    withholding_type = fields.Selection(
        selection_add=([
            ('tabla_islr', 'Tabla ISLR'),
            ('partner_tax', 'Alícuota en el Partner'),
        ])
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
                int(x.balance) * -1.0 for x in payment_group.to_pay_move_line_ids][0]
            amount = base_amount * (alicuota)
            vals['comment_withholding'] = "%s x %s" % (
                base_amount, alicuota)
            vals['total_amount'] = base_invoice
            vals['withholdable_invoiced_amount'] = payment_group.selected_debt_untaxed * -1.0
            vals['withholdable_base_amount'] = base_amount
            vals['period_withholding_amount'] = amount

        elif self.withholding_type == 'tabla_islr':
            regimen = payment_group.regimen_islr_id
            vals = super(AccountTax, self).get_withholding_vals(
                payment_group, force_withholding_amount_type)

            base = payment_group.selected_debt_untaxed * -1.0
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
                withholding = (base_withholding * withholding_percentage) - subtracting
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
