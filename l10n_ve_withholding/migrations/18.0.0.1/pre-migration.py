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


def _columns_exist(cr, table, columns):
    return all(_column_exists(cr, table, column) for column in columns)


def _create_index(cr, table, name, columns, where=None):
    if not _table_exists(cr, table) or not _columns_exist(cr, table, columns):
        _logger.info("Skipping index %s: %s.%s is not available", name, table, columns)
        return
    where_clause = " WHERE %s" % where if where else ""
    cr.execute(
        """
        CREATE INDEX IF NOT EXISTS %(name)s
            ON %(table)s (%(columns)s)
            %(where)s
        """
        % {
            "name": name,
            "table": table,
            "columns": ", ".join(columns),
            "where": where_clause,
        }
    )
    _logger.info("Ensured migration helper index %s", name)


def _log_count(cr, label, query, params=None):
    try:
        cr.execute(query, params or ())
        row = cr.fetchone()
        _logger.info("%s: %s", label, row[0] if row else 0)
    except Exception:
        _logger.exception("Could not compute migration preflight count: %s", label)


def migrate(cr, version):
    if version is None:
        return

    _logger.info("Preparing l10n_ve_withholding data migration helpers")

    _create_index(cr, "account_payment", "tmp_l10n_ve_mig_ap_group_idx", ["payment_group_id"])
    _create_index(
        cr,
        "account_payment",
        "tmp_l10n_ve_mig_ap_group_tax_idx",
        ["payment_group_id", "tax_withholding_id"],
    )
    _create_index(
        cr,
        "account_move_line_payment_group_to_pay_rel",
        "tmp_l10n_ve_mig_pg_to_pay_idx",
        ["payment_group_id", "to_pay_line_id"],
    )
    _create_index(
        cr,
        "account_move_line",
        "tmp_l10n_ve_mig_aml_move_tax_idx",
        ["move_id", "tax_line_id"],
    )
    _create_index(
        cr,
        "withholding_distribution",
        "tmp_l10n_ve_mig_wdist_payment_idx",
        ["payment_id"],
    )

    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS l10n_ve_migration_payment_withholding_map (
            old_payment_id integer PRIMARY KEY,
            withholding_id integer NOT NULL UNIQUE,
            create_date timestamp without time zone DEFAULT now()
        )
        """
    )

    if _table_exists(cr, "account_payment_group"):
        _log_count(cr, "Old payment groups", "SELECT COUNT(*) FROM account_payment_group")

    if _table_exists(cr, "account_payment") and _column_exists(cr, "account_payment", "payment_group_id"):
        _log_count(
            cr,
            "Payments linked to old groups",
            "SELECT COUNT(*) FROM account_payment WHERE payment_group_id IS NOT NULL",
        )

    if _table_exists(cr, "account_payment") and _column_exists(cr, "account_payment", "tax_withholding_id"):
        _log_count(
            cr,
            "Old withholding payments",
            "SELECT COUNT(*) FROM account_payment WHERE tax_withholding_id IS NOT NULL",
        )

    if _table_exists(cr, "account_move_line_payment_group_to_pay_rel"):
        _log_count(
            cr,
            "Old group to-pay line links",
            "SELECT COUNT(*) FROM account_move_line_payment_group_to_pay_rel",
        )
