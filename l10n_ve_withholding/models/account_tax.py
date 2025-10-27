# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2022-Present.
#
#
###############################################################################
from odoo import models, fields, _, api

import logging

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    # amount_type = fields.Selection(
    #     selection_add=([
    #         ('partner_tax', 'Alícuota en el Partner'),
    #     ]), ondelete={'partner_tax': 'set default'}
    # )
    l10n_ve_type_tax_use = fields.Selection(
        selection=[
            ('sale', 'Sales'),
            ('purchase', 'Purchases'),
            ('none', 'Other'),
            ('supplier', 'Vendor Payment Withholding'),
            ('customer', 'Customer Payment Withholding')
        ],
        compute='_compute_l10n_ve_type_tax_use', inverse='_inverse_l10n_ve_type_tax_use',
        string='Venezuela Tax Type'
    )
    l10n_ve_withholding_payment_type = fields.Selection(
        selection=[
            ('supplier', 'Vendor Payment'),
            ('customer', 'Customer Payment')
        ],
        string='Venezuela Withholding Payment Type',
    )
    l10n_ve_withholding_sequence_id = fields.Many2one(
        'ir.sequence',
        string='WTH Sequence',
        copy=False,
        check_company=True,
    )
    l10n_ve_tax_type = fields.Selection(
        selection=[
            ('tabla_islr', 'Tabla ISLR'),
            ('partner_tax', 'Alícuota en el Partner'),
        ],
        string='Tipo de Retención'
    )

    @api.depends('type_tax_use', 'l10n_ve_withholding_payment_type')
    def _compute_l10n_ve_type_tax_use(self):
        for tax in self:
            if tax.country_code == 'VE':
                if tax.type_tax_use in ('sale', 'purchase'):
                    tax.l10n_ve_type_tax_use = tax.type_tax_use
                elif tax.l10n_ve_withholding_payment_type in ('supplier', 'customer'):
                    tax.l10n_ve_type_tax_use = tax.l10n_ve_withholding_payment_type
                else:
                    tax.l10n_ve_type_tax_use = 'none'
            else:
                tax.l10n_ve_type_tax_use = 'none'

    @api.onchange('l10n_ve_type_tax_use')
    def _inverse_l10n_ve_type_tax_use(self):
        for tax in self.filtered(lambda t: t.country_code == 'VE'):
            if tax.l10n_ve_type_tax_use in ('sale', 'purchase'):
                tax.type_tax_use = tax.l10n_ve_type_tax_use
                tax.l10n_ve_tax_type = False
                tax.l10n_ve_withholding_payment_type = False
            else:
                if tax.l10n_ve_type_tax_use in ('supplier', 'customer'):
                    tax.l10n_ve_withholding_payment_type = tax.l10n_ve_type_tax_use
                else:
                    tax.l10n_ve_withholding_payment_type = False
                    tax.l10n_ve_tax_type = False
                tax.type_tax_use = 'none'
