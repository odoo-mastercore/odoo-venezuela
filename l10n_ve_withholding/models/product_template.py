# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2022-Present.
# License LGPL-3.0 or later (http: //www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    l10n_ve_disable_islr = fields.Boolean(
        string='No sujeto a ISLR',
        default=False
    )