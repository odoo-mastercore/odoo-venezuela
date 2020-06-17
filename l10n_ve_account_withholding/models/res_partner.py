###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models, fields
import logging
# from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    retencion_iva = fields.Selection([
        ('0', 'Imposibilidad de Retención'),
        ('75', ' 75%'),
        ('100', '100%'),
    ],
        'Retención I.V.A',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )