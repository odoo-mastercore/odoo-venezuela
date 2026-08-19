# -*- coding: utf-8 -*-
"""Reactiva el formulario del libro de IVA desactivado durante el upgrade."""
import logging


_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """
        UPDATE ir_ui_view view
           SET active = TRUE
          FROM ir_model_data data
         WHERE data.module = 'l10n_ve_vat_ledger'
           AND data.name = 'account_vat_ledger_form'
           AND data.model = 'ir.ui.view'
           AND view.id = data.res_id
           AND view.active IS DISTINCT FROM TRUE
        """
    )
    _logger.info(
        "l10n_ve_vat_ledger: %s vista form de libro de IVA reactivada",
        cr.rowcount,
    )
