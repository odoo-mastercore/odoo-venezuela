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

    vat_retention = fields.Selection([
        ('75', ' 75%'),
        ('100', '100%'),
    ],
        'Retención I.V.A',
    )
    seniat_partner_type_id = fields.Many2one(
        'seniat.partner.type', 
        'Tipo de persona para la retención ISLR',
    )
    seniat_regimen_islr_ids = fields.Many2many(
        'seniat.tabla.islr',
        'seniat_tabla_islr_partner_rel',
        'partner_id', 'seniat_tabla_islr_id',
        string='Régimen ISLR Aplicar',
        domain="[('seniat_partner_type_id', '=', seniat_partner_type_id)]",
    )
