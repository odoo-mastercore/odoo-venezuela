# -*- coding: utf-8 -*-
"""Rellena withholding_ids en los libros de IVA venidos de 15.

El sintoma
----------
La columna "IVA Retenido" del libro de IVA de Ventas trae cifras en 15 y sale
vacia en 18, aunque los asientos y las retenciones si se migraron.

Por que pasa
------------
withholding_ids es un Many2many calculado y almacenado. En 15 no existia: el
xlsx buscaba las retenciones en vivo contra account.payment cada vez que se
imprimia (report/account_vat_ledger_xlsx.py). Al aparecer en 18, Odoo lo
calcula una vez para los registros que ya estaban, durante el propio upgrade.

Y ahi esta el problema. Su dominio pide

    ('payment_id.state', 'in', ['in_process', 'paid'])

y account.payment.state en 18 es a su vez un campo calculado y almacenado, que
en ese momento de la conversion todavia no tiene valor definitivo. La busqueda
devuelve vacio, se almacena vacio, y como las dependencias declaradas
(journal_ids, date_from, date_to, company_id, type) no vuelven a cambiar en un
libro ya presentado, nunca se recalcula.

invoice_ids, que se calcula en el mismo metodo, si quedo bien: filtra por
account_move.state, que llega migrado desde el principio.

Que hace este script
--------------------
Rellena la relacion reproduciendo el dominio de _compute_invoices, ya con todo
calculado. Va en 'end' justo por eso: corre cuando se ha procesado el ultimo
modulo.

No se recalcula el campo por ORM a proposito. _compute_invoices reescribe
tambien invoice_ids, y estos libros estan presentados: cambiar las facturas de
un libro legal ya declarado no es cosa de un script de migracion. Aqui solo se
añade lo que falta.
"""
import logging

_logger = logging.getLogger(__name__)


def _table_exists(cr, table):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.tables
         WHERE table_schema = 'public'
           AND table_name = %s
        """,
        (table,),
    )
    return bool(cr.fetchone())


def migrate(cr, version):
    if not version:
        return

    required = ('account_vat_ledger',
                'account_vat_ledger_l10n_ve_payment_withholding_rel',
                'l10n_ve_payment_withholding',
                'account_payment',
                'account_tax')
    missing = [table for table in required if not _table_exists(cr, table)]
    if missing:
        _logger.info(
            "l10n_ve_vat_ledger: no se rellenan las retenciones, faltan %s.",
            ', '.join(missing))
        return

    cr.execute(
        """
        INSERT INTO account_vat_ledger_l10n_ve_payment_withholding_rel
                    (account_vat_ledger_id, l10n_ve_payment_withholding_id)
        SELECT ledger.id, withholding.id
          FROM account_vat_ledger ledger
          JOIN account_payment payment
            ON payment.state IN ('in_process', 'paid')
           AND (payment.company_id = ledger.company_id
                OR payment.company_id IN (SELECT company.id
                                            FROM res_company company
                                           WHERE company.parent_id = ledger.company_id))
          JOIN l10n_ve_payment_withholding withholding
            ON withholding.payment_id = payment.id
          JOIN account_tax tax
            ON tax.id = withholding.tax_id
           AND tax.l10n_ve_withholding_ingoing_type = 'iva'
         WHERE ledger.date_from IS NOT NULL
           AND ledger.date_to IS NOT NULL
           AND (
                -- Ventas: la retencion entra por su fecha o por la del pago,
                -- que no siempre coinciden.
                (ledger.type = 'sale'
                 AND tax.l10n_ve_withholding_payment_type = 'customer'
                 AND (withholding.date BETWEEN ledger.date_from AND ledger.date_to
                      OR payment.date BETWEEN ledger.date_from AND ledger.date_to))
                OR
                -- Compras: solo por la fecha de la retencion.
                (ledger.type = 'purchase'
                 AND tax.l10n_ve_withholding_payment_type = 'supplier'
                 AND withholding.date BETWEEN ledger.date_from AND ledger.date_to)
           )
           AND NOT EXISTS (
               SELECT 1
                 FROM account_vat_ledger_l10n_ve_payment_withholding_rel existing
                WHERE existing.account_vat_ledger_id = ledger.id
                  AND existing.l10n_ve_payment_withholding_id = withholding.id
           )
        """
    )
    linked = cr.rowcount
    if not linked:
        _logger.info(
            "l10n_ve_vat_ledger: no habia retenciones que enlazar a los libros.")
        return

    cr.execute(
        """
        SELECT ledger.type, count(DISTINCT ledger.id), count(*)
          FROM account_vat_ledger_l10n_ve_payment_withholding_rel rel
          JOIN account_vat_ledger ledger ON ledger.id = rel.account_vat_ledger_id
      GROUP BY ledger.type
      ORDER BY ledger.type
        """
    )
    for ledger_type, ledgers, withholdings in cr.fetchall():
        _logger.info(
            "l10n_ve_vat_ledger: libros de %s con retenciones: %s (%s retencion(es)).",
            ledger_type, ledgers, withholdings)
    _logger.info(
        "l10n_ve_vat_ledger: %s enlace(s) libro-retencion creados.", linked)
