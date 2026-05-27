# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class L10nVePartnerTax(models.Model):
    _name = "l10n_ve.partner.tax"
    _description = "Venezuela Partner Taxes"
    _order = "tax_id"
    _check_company_auto = True
    _check_company_domain = models.check_company_domain_parent_of

    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='cascade',
        check_company=True,
        string="Partner"
    )
    tax_id = fields.Many2one(
        'account.tax',
        required=True,
        string="Tax",
    )
    company_id = fields.Many2one(
        related='tax_id.company_id', store=True,
    )

    @api.constrains('partner_id', 'tax_id')
    def _check_unique_partner_tax(self):
        for record in self:
            domain = [
                ('id', '!=', record.id),
                ('partner_id', '=', record.partner_id.id),
                ('tax_id', '=', record.tax_id.id),
            ]
            if self.search_count(domain):
                raise ValidationError(_(
                    'No puede configurar dos veces el mismo impuesto de retención '
                    'para el mismo contacto.'
                ))

    @api.constrains('tax_id')
    def _check_supplier_withholding_tax(self):
        for record in self:
            if record.tax_id.l10n_ve_withholding_payment_type != 'supplier':
                raise ValidationError(_(
                    'El impuesto configurado en el contacto debe ser una '
                    'retención de pago a proveedor.'
                ))
