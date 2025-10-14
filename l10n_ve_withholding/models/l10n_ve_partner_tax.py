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