###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_ve_vat_retention = fields.Selection(
        selection=[
            ('75', ' 75%'),
            ('100', '100%'),
        ],
        string='Retención I.V.A',
    )
    l10n_ve_seniat_partner_type_id = fields.Many2one(
        'seniat.partner.type',
        'Tipo de persona para la retención ISLR',
    )
    l10n_ve_seniat_regimen_islr_ids = fields.Many2many(
        'seniat.tabla.islr',
        'seniat_tabla_islr_partner_rel',
        'partner_id', 'seniat_tabla_islr_id',
        string='Régimen ISLR Aplicar',
        domain="[('seniat_partner_type_id', '=', l10n_ve_seniat_partner_type_id)]",
    )
    l10n_ve_partner_tax_ids = fields.One2many(
        'l10n_ve.partner.tax',
        'partner_id',
        'Venezuela Withholding Taxes',
        domain=[('tax_id.l10n_ve_withholding_payment_type', '=', 'supplier')]
    )
