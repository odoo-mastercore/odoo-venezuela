from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    def _localization_use_withholdings(self):
        """ This method is to be inherited by localizations and return True 
            if localization use documents """
        self.ensure_one()
        if self.country_id == self.env.ref('base.ve'):
            return True
        else:
            return False
