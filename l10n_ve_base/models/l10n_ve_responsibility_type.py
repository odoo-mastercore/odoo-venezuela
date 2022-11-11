# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################

from odoo import models, fields

#Reference to
#www.tipsparaempresas.com/tipos-de-contribuyentes-de-impuestos-al-seniat/
class L10nVeResponsibilityType(models.Model):

    _name = 'l10n_ve.responsibility.type'
    _description = 'SENIAT Responsibility Type'
    _order = 'sequence'

    name = fields.Char(required=True, index=True)
    sequence = fields.Integer()
    code = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [('name', 'unique(name)', 'Name must be unique!'),
                        ('code', 'unique(code)', 'Code must be unique!')]
