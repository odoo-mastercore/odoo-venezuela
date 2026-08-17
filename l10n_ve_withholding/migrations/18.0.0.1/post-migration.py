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


def _column_exists(cr, table, column):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = %s
           AND column_name = %s
        """,
        (table, column),
    )
    return bool(cr.fetchone())


def _relation_columns(cr, table):
    cr.execute(
        """
        SELECT column_name
          FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = %s
        """,
        (table,),
    )
    return {row[0] for row in cr.fetchall()}


def _log_count(cr, label, query, params=None):
    try:
        cr.execute(query, params or ())
        row = cr.fetchone()
        _logger.info("%s: %s", label, row[0] if row else 0)
    except Exception:
        _logger.exception("Could not compute migration count: %s", label)


def _execute_if_tables(cr, label, tables, query, params=None):
    missing = [table for table in tables if not _table_exists(cr, table)]
    if missing:
        _logger.info("Skipping %s: missing tables %s", label, ", ".join(missing))
        return
    cr.execute(query, params or ())
    _logger.info("%s: %s rows affected", label, cr.rowcount)


def _update_renamed_column(cr, table, old, new, where=None):
    if not (_table_exists(cr, table) and _column_exists(cr, table, old) and _column_exists(cr, table, new)):
        return
    where_clause = "AND (%s)" % where if where else ""
    cr.execute(
        """
        UPDATE %(table)s
           SET %(new)s = %(old)s
         WHERE %(old)s IS NOT NULL
           AND %(new)s IS DISTINCT FROM %(old)s
           %(where)s
        """
        % {"table": table, "old": old, "new": new, "where": where_clause}
    )
    _logger.info("Migrated %s.%s -> %s: %s rows", table, old, new, cr.rowcount)


def _clean_invalid_tax_type(cr):
    """Leave l10n_ve_tax_type with values that exist in the 18 selection.

    withholding_type in 15 was a selection_add on top of account_withholding,
    a module that 18 no longer has, so it carried values -- 'none' among them
    -- that the new selection (tabla_islr, partner_tax) does not define.
    Copying the column verbatim brings them over and the field ends up holding
    something Odoo cannot render.

    They are cleared instead of guessed: 'none' means the tax was never typed
    in 15, and inferring a type from the tax name would be a coin flip. The
    ones affected are logged so somebody can type them by hand -- withholding
    on sales, which Conext receives rather than issues, so no certificate of
    ours depends on them.
    """
    if not _column_exists(cr, "account_tax", "l10n_ve_tax_type"):
        return

    cr.execute(
        """
        SELECT id, name->>'en_US', l10n_ve_tax_type
          FROM account_tax
         WHERE l10n_ve_tax_type IS NOT NULL
           AND l10n_ve_tax_type NOT IN ('tabla_islr', 'partner_tax')
        """
    )
    rows = cr.fetchall()
    if not rows:
        return

    cr.execute(
        """
        UPDATE account_tax
           SET l10n_ve_tax_type = NULL
         WHERE l10n_ve_tax_type IS NOT NULL
           AND l10n_ve_tax_type NOT IN ('tabla_islr', 'partner_tax')
        """
    )
    _logger.warning(
        "Cleared l10n_ve_tax_type on %s tax(es) whose 15 value is not in the "
        "18 selection: %s", len(rows),
        ", ".join("%s (id %s, was '%s')" % (name, tax_id, old)
                  for tax_id, name, old in rows))


def _migrate_renamed_fields(cr):
    _update_renamed_column(cr, "res_partner", "vat_retention", "l10n_ve_vat_retention")
    _update_renamed_column(
        cr,
        "res_partner",
        "seniat_partner_type_id",
        "l10n_ve_seniat_partner_type_id",
    )
    _update_renamed_column(cr, "account_journal", "sequence_control_id", "l10n_ve_sequence_control_id")
    _update_renamed_column(cr, "account_journal", "apply_iva", "l10n_ve_apply_iva")
    _update_renamed_column(cr, "account_journal", "apply_islr", "l10n_ve_apply_islr")
    _update_renamed_column(cr, "account_move", "l10n_ve_document_number", "l10n_ve_control_number")
    _update_renamed_column(cr, "product_template", "disable_islr", "l10n_ve_disable_islr")
    _update_renamed_column(cr, "account_tax", "withholding_sequence_id", "l10n_ve_withholding_sequence_id")
    _update_renamed_column(cr, "account_tax", "withholding_type", "l10n_ve_tax_type")
    _clean_invalid_tax_type(cr)

    if not _table_exists(cr, "account_tax"):
        return
    if _column_exists(cr, "account_tax", "l10n_ve_withholding_payment_type") and _column_exists(
        cr, "account_tax", "type_tax_use"
    ):
        cr.execute(
            """
            UPDATE account_tax
               SET l10n_ve_withholding_payment_type = type_tax_use
             WHERE type_tax_use IN ('supplier', 'customer')
               AND (
                    l10n_ve_withholding_payment_type IS NULL
                    OR l10n_ve_withholding_payment_type IS DISTINCT FROM type_tax_use
               )
            """
        )
        _logger.info("Migrated withholding tax payment type: %s rows", cr.rowcount)
        cr.execute(
            """
            UPDATE account_tax
               SET type_tax_use = 'none'
             WHERE type_tax_use IN ('supplier', 'customer')
            """
        )
        _logger.info("Normalized withholding tax type_tax_use: %s rows", cr.rowcount)


def _migrate_partner_tax_config(cr):
    required = [
        _table_exists(cr, "l10n_ve_partner_tax"),
        _table_exists(cr, "res_partner"),
        _table_exists(cr, "account_tax"),
        _column_exists(cr, "res_partner", "l10n_ve_vat_retention"),
        _column_exists(cr, "account_tax", "l10n_ve_tax_type"),
        _column_exists(cr, "account_tax", "l10n_ve_withholding_payment_type"),
    ]
    if not all(required):
        _logger.info("Skipping partner VAT retention config migration: required structures are unavailable")
        return

    company_filter = ""
    if _column_exists(cr, "account_tax", "company_id") and _column_exists(cr, "res_partner", "company_id"):
        company_filter = """
           AND (tax.company_id IS NULL
                OR tax.company_id = partner.company_id
                OR partner.company_id IS NULL)
        """

    insert_columns = ["create_uid", "create_date", "write_uid", "write_date", "partner_id", "tax_id"]
    select_columns = ["1", "now()", "1", "now()", "partner.id", "tax.id"]
    if _column_exists(cr, "l10n_ve_partner_tax", "company_id") and _column_exists(cr, "account_tax", "company_id"):
        insert_columns.append("company_id")
        select_columns.append("tax.company_id")

    cr.execute(
        """
        INSERT INTO l10n_ve_partner_tax (%(insert_columns)s)
        SELECT %(select_columns)s
          FROM res_partner partner
          JOIN account_tax tax
            ON tax.l10n_ve_tax_type = 'partner_tax'
           AND tax.l10n_ve_withholding_payment_type = 'supplier'
         WHERE partner.l10n_ve_vat_retention IS NOT NULL
           AND partner.l10n_ve_vat_retention <> ''
           %(company_filter)s
           AND NOT EXISTS (
               SELECT 1
                 FROM l10n_ve_partner_tax existing
                WHERE existing.partner_id = partner.id
                  AND existing.tax_id = tax.id
           )
        """
        % {
            "company_filter": company_filter,
            "insert_columns": ", ".join(insert_columns),
            "select_columns": ", ".join(select_columns),
        }
    )
    _logger.info("Created partner VAT withholding tax config rows: %s", cr.rowcount)


def _target_payment_filter(alias="payment"):
    """Select normal payments, or one fallback for withholding-only groups."""
    if _column_exists_cached("account_payment", "tax_withholding_id"):
        return """
            (
                %(alias)s.tax_withholding_id IS NULL
                OR (
                    %(alias)s.id = (
                        SELECT MIN(fallback.id)
                          FROM account_payment fallback
                         WHERE fallback.payment_group_id = %(alias)s.payment_group_id
                    )
                    AND NOT EXISTS (
                        SELECT 1
                          FROM account_payment normal_payment
                         WHERE normal_payment.payment_group_id = %(alias)s.payment_group_id
                           AND normal_payment.tax_withholding_id IS NULL
                    )
                )
            )
        """ % {"alias": alias}
    return "TRUE"


_COLUMN_CACHE = {}


def _column_exists_cached(table, column):
    return _COLUMN_CACHE.get((table, column), False)


def _prime_column_cache(cr):
    cr.execute(
        """
        SELECT table_name, column_name
          FROM information_schema.columns
         WHERE table_schema = 'public'
        """
    )
    _COLUMN_CACHE.clear()
    _COLUMN_CACHE.update({(row[0], row[1]): True for row in cr.fetchall()})


def _migrate_payment_group_data(cr):
    if not (
        _table_exists(cr, "account_payment_group")
        and _table_exists(cr, "account_payment")
        and _column_exists(cr, "account_payment", "payment_group_id")
    ):
        _logger.info("Skipping payment group header migration: old payment group structures are unavailable")
        return

    assignments = []
    if _column_exists(cr, "account_payment", "date") and _column_exists(cr, "account_payment_group", "payment_date"):
        assignments.append("date = COALESCE(payment.date, payment_group.payment_date)")
    if _column_exists(cr, "account_payment", "partner_type") and _column_exists(
        cr, "account_payment_group", "partner_type"
    ):
        assignments.append("partner_type = COALESCE(payment.partner_type, payment_group.partner_type)")
    if _column_exists(cr, "account_payment", "partner_id") and _column_exists(cr, "account_payment_group", "partner_id"):
        assignments.append("partner_id = COALESCE(payment.partner_id, payment_group.partner_id)")
    if _column_exists(cr, "account_payment", "company_id") and _column_exists(cr, "account_payment_group", "company_id"):
        assignments.append("company_id = COALESCE(payment.company_id, payment_group.company_id)")
    if _column_exists(cr, "account_payment", "currency_id") and _column_exists(
        cr, "account_payment_group", "currency_id"
    ):
        assignments.append("currency_id = COALESCE(payment.currency_id, payment_group.currency_id)")
    if _column_exists(cr, "account_payment", "receiptbook_id") and _column_exists(
        cr, "account_payment_group", "receiptbook_id"
    ):
        assignments.append("receiptbook_id = COALESCE(payment.receiptbook_id, payment_group.receiptbook_id)")
    if _column_exists(cr, "account_payment", "unreconciled_amount") and _column_exists(
        cr, "account_payment_group", "unreconciled_amount"
    ):
        assignments.append(
            """
            unreconciled_amount = CASE
                WHEN COALESCE(payment.unreconciled_amount, 0.0) = 0.0
                    THEN COALESCE(payment_group.unreconciled_amount, 0.0)
                ELSE payment.unreconciled_amount
            END
            """
        )

    if not assignments:
        _logger.info("Skipping payment group header migration: no compatible target columns found")
        return

    cr.execute(
        """
        UPDATE account_payment payment
           SET %(assignments)s
          FROM account_payment_group payment_group
         WHERE payment.payment_group_id = payment_group.id
           AND %(principal_filter)s
        """
        % {
            "assignments": ", ".join(assignments),
            "principal_filter": _target_payment_filter("payment"),
        }
    )
    _logger.info("Migrated old payment group header data to account.payment: %s rows", cr.rowcount)


def _migrate_to_pay_lines(cr):
    required = [
        _table_exists(cr, "account_move_line_payment_group_to_pay_rel"),
        _table_exists(cr, "account_move_line_payment_to_pay_rel"),
        _table_exists(cr, "account_payment"),
        _column_exists(cr, "account_payment", "payment_group_id"),
    ]
    if not all(required):
        _logger.info("Skipping payment to-pay line migration: required structures are unavailable")
        return

    _execute_if_tables(
        cr,
        "Migrated old payment group to-pay lines",
        ["account_move_line_payment_group_to_pay_rel", "account_move_line_payment_to_pay_rel", "account_payment"],
        """
        INSERT INTO account_move_line_payment_to_pay_rel (payment_id, to_pay_line_id)
        SELECT DISTINCT payment.id, old_rel.to_pay_line_id
          FROM account_payment payment
          JOIN account_move_line_payment_group_to_pay_rel old_rel
            ON old_rel.payment_group_id = payment.payment_group_id
         WHERE payment.payment_group_id IS NOT NULL
           AND %(principal_filter)s
           AND NOT EXISTS (
               SELECT 1
                 FROM account_move_line_payment_to_pay_rel existing
                WHERE existing.payment_id = payment.id
                  AND existing.to_pay_line_id = old_rel.to_pay_line_id
           )
        """
        % {"principal_filter": _target_payment_filter("payment")},
    )


def _ensure_withholding_map_table(cr):
    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS l10n_ve_migration_payment_withholding_map (
            old_payment_id integer PRIMARY KEY,
            withholding_id integer NOT NULL UNIQUE,
            create_date timestamp without time zone DEFAULT now()
        )
        """
    )


def _field_expr(cr, table, column, fallback="NULL"):
    return column if _column_exists(cr, table, column) else fallback


def _old_payment_col(cr, column, fallback="NULL"):
    return "withholding_payment.%s" % column if _column_exists(cr, "account_payment", column) else fallback


def _payment_name_expr(cr):
    if _column_exists(cr, "account_payment", "name"):
        return "COALESCE(main_payment.name, main_payment.id::varchar)"
    return "main_payment.id::varchar"


def _old_payment_date_expr(cr):
    if _column_exists(cr, "account_payment", "date"):
        return "COALESCE(withholding_payment.date, main_payment.date, CURRENT_DATE)"
    return "CURRENT_DATE"


def _old_state_expr(cr):
    if not _column_exists(cr, "account_payment", "state"):
        return "'posted'"
    return """
        CASE
            WHEN withholding_payment.state IN ('cancel', 'cancelled', 'canceled') THEN 'cancel'
            WHEN withholding_payment.state = 'draft' THEN 'draft'
            ELSE 'posted'
        END
    """


def _tax_type_expr(cr):
    if _column_exists(cr, "account_tax", "l10n_ve_tax_type"):
        return "tax.l10n_ve_tax_type"
    if _column_exists(cr, "account_tax", "withholding_type"):
        return "tax.withholding_type"
    return "NULL"


def _withholding_base_expr(cr):
    candidates = []
    for column in ("withholding_base_amount", "withholdable_base_amount", "total_amount"):
        if _column_exists(cr, "account_payment", column):
            candidates.append("NULLIF(withholding_payment.%s, 0.0)" % column)
    candidates.append("0.0")
    return "COALESCE(%s)" % ", ".join(candidates)


def _withholding_amount_expr(cr):
    candidates = []
    for column in ("computed_withholding_amount", "amount"):
        if _column_exists(cr, "account_payment", column):
            candidates.append("NULLIF(withholding_payment.%s, 0.0)" % column)
    candidates.append("0.0")
    return "COALESCE(%s)" % ", ".join(candidates)


def _insert_existing_withholding_map(cr):
    if not (
        _table_exists(cr, "account_payment")
        and _table_exists(cr, "account_tax")
        and _table_exists(cr, "l10n_ve_payment_withholding")
        and _column_exists(cr, "account_payment", "tax_withholding_id")
        and _column_exists(cr, "account_payment", "payment_group_id")
    ):
        return

    name_expr = _old_payment_col(cr, "withholding_number", "'/'")
    amount_expr = _withholding_amount_expr(cr)
    wh_name_column = "name" if _column_exists(cr, "l10n_ve_payment_withholding", "name") else None
    if not all(
        _column_exists(cr, "l10n_ve_payment_withholding", column)
        for column in ("payment_id", "tax_id", "amount")
    ):
        return

    name_match = (
        "COALESCE(existing.name, '/') = COALESCE(%s, '/')" % name_expr
        if wh_name_column and name_expr != "'/'"
        else "TRUE"
    )

    cr.execute(
        """
        WITH principal_payment AS (
            SELECT payment_group_id, MIN(id) AS payment_id
              FROM account_payment payment
             WHERE payment_group_id IS NOT NULL
               AND %(principal_filter)s
             GROUP BY payment_group_id
        )
        INSERT INTO l10n_ve_migration_payment_withholding_map (old_payment_id, withholding_id)
        SELECT withholding_payment.id, MIN(existing.id)
          FROM account_payment withholding_payment
          JOIN principal_payment principal
            ON principal.payment_group_id = withholding_payment.payment_group_id
          JOIN l10n_ve_payment_withholding existing
            ON existing.payment_id = principal.payment_id
           AND existing.tax_id = withholding_payment.tax_withholding_id
           AND %(name_match)s
           AND ABS(COALESCE(existing.amount, 0.0) - (%(amount_expr)s)) < 0.01
         WHERE withholding_payment.tax_withholding_id IS NOT NULL
           AND NOT EXISTS (
               SELECT 1
                 FROM l10n_ve_migration_payment_withholding_map mapped
                WHERE mapped.old_payment_id = withholding_payment.id
           )
         GROUP BY withholding_payment.id
        """
        % {
            "principal_filter": _target_payment_filter("payment"),
            "name_match": name_match,
            "amount_expr": amount_expr,
        }
    )
    _logger.info("Mapped pre-existing withholding rows: %s", cr.rowcount)


def _migrate_withholding_lines(cr):
    required = [
        _table_exists(cr, "account_payment"),
        _table_exists(cr, "account_payment_group"),
        _table_exists(cr, "account_tax"),
        _table_exists(cr, "l10n_ve_payment_withholding"),
        _column_exists(cr, "account_payment", "tax_withholding_id"),
        _column_exists(cr, "account_payment", "payment_group_id"),
    ]
    if not all(required):
        _logger.info("Skipping withholding payment migration: required structures are unavailable")
        return

    _ensure_withholding_map_table(cr)
    _insert_existing_withholding_map(cr)

    target_columns = _relation_columns(cr, "l10n_ve_payment_withholding")
    insert_columns = ["id", "create_uid", "create_date", "write_uid", "write_date"]
    select_exprs = [
        "nextval(pg_get_serial_sequence('l10n_ve_payment_withholding', 'id')) AS id",
        "1 AS create_uid",
        "now() AS create_date",
        "1 AS write_uid",
        "now() AS write_date",
    ]

    column_exprs = {
        "payment_id": "main_payment.id",
        "tax_id": "withholding_payment.tax_withholding_id",
        "state": _old_state_expr(cr),
        "name": "COALESCE(%s, '/')" % _old_payment_col(cr, "withholding_number"),
        "payment_name": _payment_name_expr(cr),
        "payment_date": _old_payment_date_expr(cr),
        "payment_type": _old_payment_col(cr, "payment_type", "main_payment.payment_type"),
        "partner_type": _old_payment_col(cr, "partner_type", "main_payment.partner_type"),
        "ref": _old_payment_col(cr, "comment_withholding"),
        "base_amount": _withholding_base_expr(cr),
        "amount": _withholding_amount_expr(cr),
        "l10n_ve_concept_withholding": _old_payment_col(cr, "concept_withholding"),
        "calc_islr": "CASE WHEN %(tax_type)s = 'tabla_islr' THEN 'all' ELSE NULL END" % {"tax_type": _tax_type_expr(cr)},
        "date": _old_payment_date_expr(cr),
    }
    if _column_exists(cr, "account_payment_group", "regimen_islr_id"):
        column_exprs["l10n_ve_regimen_islr_id"] = (
            "CASE WHEN %(tax_type)s = 'tabla_islr' THEN payment_group.regimen_islr_id ELSE NULL END"
            % {"tax_type": _tax_type_expr(cr)}
        )

    for column, expr in column_exprs.items():
        if column in target_columns:
            insert_columns.append(column)
            select_exprs.append("%s AS %s" % (expr, column))

    cr.execute(
        """
        WITH principal_payment AS (
            SELECT payment_group_id, MIN(id) AS payment_id
              FROM account_payment payment
             WHERE payment_group_id IS NOT NULL
               AND %(principal_filter)s
             GROUP BY payment_group_id
        ),
        rows_to_create AS (
            SELECT withholding_payment.id AS old_payment_id,
                   %(select_exprs)s
              FROM account_payment withholding_payment
              JOIN principal_payment principal
                ON principal.payment_group_id = withholding_payment.payment_group_id
              JOIN account_payment main_payment
                ON main_payment.id = principal.payment_id
              JOIN account_tax tax
                ON tax.id = withholding_payment.tax_withholding_id
              LEFT JOIN account_payment_group payment_group
                ON payment_group.id = withholding_payment.payment_group_id
             WHERE withholding_payment.tax_withholding_id IS NOT NULL
               AND NOT EXISTS (
                   SELECT 1
                     FROM l10n_ve_migration_payment_withholding_map mapped
                    WHERE mapped.old_payment_id = withholding_payment.id
               )
        ),
        inserted AS (
            INSERT INTO l10n_ve_payment_withholding (%(insert_columns)s)
            SELECT %(insert_columns)s
              FROM rows_to_create
            RETURNING id
        )
        INSERT INTO l10n_ve_migration_payment_withholding_map (old_payment_id, withholding_id)
        SELECT rows_to_create.old_payment_id, rows_to_create.id
          FROM rows_to_create
         WHERE NOT EXISTS (
             SELECT 1
               FROM l10n_ve_migration_payment_withholding_map mapped
              WHERE mapped.old_payment_id = rows_to_create.old_payment_id
         )
        """
        % {
            "principal_filter": _target_payment_filter("payment"),
            "select_exprs": ", ".join(select_exprs),
            "insert_columns": ", ".join(insert_columns),
        }
    )
    _logger.info("Created withholding rows from old withholding payments: %s", cr.rowcount)


def _link_withholding_moves(cr):
    required = [
        _table_exists(cr, "payment_withholding_move_rel"),
        _table_exists(cr, "l10n_ve_migration_payment_withholding_map"),
        _table_exists(cr, "account_payment"),
        _table_exists(cr, "account_move_line"),
        _table_exists(cr, "account_move_line_payment_group_to_pay_rel"),
        _column_exists(cr, "account_payment", "payment_group_id"),
    ]
    if not all(required):
        _logger.info("Skipping withholding invoice links: required structures are unavailable")
        return

    cr.execute(
        """
        INSERT INTO payment_withholding_move_rel (withholding_id, move_id)
        SELECT DISTINCT line.move_id, mapped.withholding_id
          FROM l10n_ve_migration_payment_withholding_map mapped
          JOIN account_payment old_withholding
            ON old_withholding.id = mapped.old_payment_id
          JOIN account_move_line_payment_group_to_pay_rel old_rel
            ON old_rel.payment_group_id = old_withholding.payment_group_id
          JOIN account_move_line line
            ON line.id = old_rel.to_pay_line_id
         WHERE line.move_id IS NOT NULL
           AND NOT EXISTS (
               SELECT 1
                 FROM payment_withholding_move_rel existing
                WHERE existing.withholding_id = line.move_id
                  AND existing.move_id = mapped.withholding_id
           )
        """
    )
    _logger.info("Linked withholding rows to historical invoices: %s", cr.rowcount)


def _link_vat_tax_lines(cr):
    required = [
        _table_exists(cr, "move_account_payment_wth_line_rel"),
        _table_exists(cr, "l10n_ve_migration_payment_withholding_map"),
        _table_exists(cr, "account_payment"),
        _table_exists(cr, "account_tax"),
        _table_exists(cr, "account_move_line"),
        _table_exists(cr, "account_move_line_payment_group_to_pay_rel"),
        _column_exists(cr, "account_payment", "payment_group_id"),
        _column_exists(cr, "account_payment", "tax_withholding_id"),
        _column_exists(cr, "account_move_line", "tax_line_id"),
    ]
    if not all(required):
        _logger.info("Skipping VAT tax line links: required structures are unavailable")
        return

    # 'iva' no es un valor de este campo, ni en 15 ni en 18: la seleccion es
    # tabla_islr / partner_tax. La retencion de IVA es la que toma la alicuota
    # del partner -- el 75 o el 100 de res_partner.l10n_ve_vat_retention --, o
    # sea partner_tax; tabla_islr es la de ISLR.
    #
    # Con 'iva' el INSERT no casaba ninguna fila, la relacion
    # move_account_payment_wth_line_rel quedaba vacia y el comprobante de
    # retencion salia impreso pero sin detalle, con TOTALES en 0,00.
    tax_type_filter = "FALSE"
    if _column_exists(cr, "account_tax", "l10n_ve_tax_type"):
        tax_type_filter = "withholding_tax.l10n_ve_tax_type = 'partner_tax'"
    elif _column_exists(cr, "account_tax", "withholding_type"):
        tax_type_filter = "withholding_tax.withholding_type = 'partner_tax'"

    cr.execute(
        """
        WITH principal_payment AS (
            SELECT payment_group_id, MIN(id) AS payment_id
              FROM account_payment payment
             WHERE payment_group_id IS NOT NULL
               AND %(principal_filter)s
             GROUP BY payment_group_id
        )
        INSERT INTO move_account_payment_wth_line_rel (move_line_id, payment_id)
        SELECT DISTINCT principal.payment_id, tax_line.id
          FROM l10n_ve_migration_payment_withholding_map mapped
          JOIN account_payment old_withholding
            ON old_withholding.id = mapped.old_payment_id
          JOIN account_tax withholding_tax
            ON withholding_tax.id = old_withholding.tax_withholding_id
          JOIN principal_payment principal
            ON principal.payment_group_id = old_withholding.payment_group_id
          JOIN account_move_line_payment_group_to_pay_rel old_rel
            ON old_rel.payment_group_id = old_withholding.payment_group_id
          JOIN account_move_line selected_line
            ON selected_line.id = old_rel.to_pay_line_id
          JOIN account_move_line tax_line
            ON tax_line.move_id = selected_line.move_id
           AND tax_line.tax_line_id IS NOT NULL
         WHERE %(tax_type_filter)s
           AND NOT EXISTS (
               SELECT 1
                 FROM move_account_payment_wth_line_rel existing
                WHERE existing.move_line_id = principal.payment_id
                  AND existing.payment_id = tax_line.id
           )
        """
        % {
            "principal_filter": _target_payment_filter("payment"),
            "tax_type_filter": tax_type_filter,
        }
    )
    _logger.info("Linked VAT withholding tax lines to principal payments: %s", cr.rowcount)


def _log_preflight_gaps(cr):
    if not (
        _table_exists(cr, "account_payment_group")
        and _table_exists(cr, "account_payment")
        and _column_exists(cr, "account_payment", "payment_group_id")
    ):
        return
    _log_count(
        cr,
        "Old payment groups without a target payment",
        """
        SELECT COUNT(*)
          FROM account_payment_group payment_group
         WHERE NOT EXISTS (
             SELECT 1
               FROM account_payment payment
              WHERE payment.payment_group_id = payment_group.id
                AND %(principal_filter)s
         )
        """
        % {"principal_filter": _target_payment_filter("payment")},
    )
    _log_count(
        cr,
        "Old payment groups with multiple normal payments",
        """
        SELECT COUNT(*)
          FROM (
              SELECT payment_group_id
                FROM account_payment payment
               WHERE payment_group_id IS NOT NULL
                 AND %(principal_filter)s
               GROUP BY payment_group_id
              HAVING COUNT(*) > 1
          ) grouped
        """
        % {"principal_filter": _target_payment_filter("payment")},
    )
    if _column_exists(cr, "account_payment", "tax_withholding_id"):
        _log_count(
            cr,
            "Old withholding payments without a target payment",
            """
            SELECT COUNT(*)
              FROM account_payment withholding_payment
             WHERE withholding_payment.tax_withholding_id IS NOT NULL
               AND NOT EXISTS (
                   SELECT 1
                     FROM account_payment payment
                    WHERE payment.payment_group_id = withholding_payment.payment_group_id
                      AND %(principal_filter)s
               )
            """
            % {"principal_filter": _target_payment_filter("payment")},
        )


def migrate(cr, version):
    if version is None:
        return

    _logger.info("Running l10n_ve_withholding data migration from Odoo 15 payment groups")
    _prime_column_cache(cr)
    _log_preflight_gaps(cr)
    _migrate_renamed_fields(cr)
    _migrate_partner_tax_config(cr)
    _migrate_payment_group_data(cr)
    _migrate_to_pay_lines(cr)
    _migrate_withholding_lines(cr)
    _link_withholding_moves(cr)
    _link_vat_tax_lines(cr)

    _log_count(
        cr,
        "Target payment to-pay line links",
        "SELECT COUNT(*) FROM account_move_line_payment_to_pay_rel"
        if _table_exists(cr, "account_move_line_payment_to_pay_rel")
        else "SELECT 0",
    )
    _log_count(
        cr,
        "Migrated withholding rows mapped",
        "SELECT COUNT(*) FROM l10n_ve_migration_payment_withholding_map"
        if _table_exists(cr, "l10n_ve_migration_payment_withholding_map")
        else "SELECT 0",
    )
