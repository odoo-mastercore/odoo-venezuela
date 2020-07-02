from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

   
    def get_taxes_values(self):
        """
        Hacemos esto para disponer de fecha de factura y cia para calcular
        impuesto con código python (por ej. para ARBA).
        Aparentemente no se puede cambiar el contexto a cosas que se llaman
        desde un onchange (ver https://github.com/odoo/odoo/issues/7472)
        entonces usamos este artilugio
        """
        invoice_date = self.invoice_date or fields.Date.context_today(self)
        # hacemos try porque al llamarse desde acciones de servidor da error
        try:
            self.env.context.invoice_date = invoice_date
            self.env.context.invoice_company = self.company_id
        except Exception:
            pass
        return super().get_taxes_values()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_price(self):
        # ver nota en get_taxes_values
        invoice = self.move_id
        invoice_date = invoice.invoice_date or fields.Date.context_today(self)
        # hacemos try porque al llamarse desde acciones de servidor da error
        try:
            self.env.context.invoice_date = invoice_date
            self.env.context.invoice_company = self.company_id
        except Exception:
            pass
        return super()._compute_price()
