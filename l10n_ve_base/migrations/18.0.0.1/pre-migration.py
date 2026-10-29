import logging


_logger = logging.getLogger(__name__)

OLD_MODULE = "territorial_pd"
NEW_MODULE = "l10n_ve_base"
TERRITORIAL_MODELS = (
    "res.country.state",
    "res.country.state.municipality",
    "res.country.state.municipality.parish",
)


def migrate(cr, version):
    if version is None:
        return

    # territorial_pd provided this catalog in Odoo 15. In Odoo 18 the same
    # records and local XML IDs belong to l10n_ve_base. Move their ownership
    # before the CSV loader runs so it updates the existing rows.
    cr.execute(
        """
        SELECT old.name, old.model, old.res_id, target.model, target.res_id
          FROM ir_model_data old
          JOIN ir_model_data target
            ON target.module = %s
           AND target.name = old.name
         WHERE old.module = %s
           AND old.model IN %s
           AND (target.model, target.res_id)
               IS DISTINCT FROM (old.model, old.res_id)
        """,
        (NEW_MODULE, OLD_MODULE, TERRITORIAL_MODELS),
    )
    conflicts = cr.fetchall()
    if conflicts:
        raise RuntimeError(
            "Conflicting territorial XML IDs while migrating %s to %s: %s"
            % (OLD_MODULE, NEW_MODULE, conflicts[:10])
        )

    # Allow the script to be retried if aliases pointing to the same records
    # were already created by an earlier attempt.
    cr.execute(
        """
        DELETE FROM ir_model_data old
              USING ir_model_data target
         WHERE old.module = %s
           AND old.model IN %s
           AND target.module = %s
           AND target.name = old.name
           AND target.model = old.model
           AND target.res_id = old.res_id
        """,
        (OLD_MODULE, TERRITORIAL_MODELS, NEW_MODULE),
    )
    removed_aliases = cr.rowcount

    cr.execute(
        """
        UPDATE ir_model_data
           SET module = %s
         WHERE module = %s
           AND model IN %s
        """,
        (NEW_MODULE, OLD_MODULE, TERRITORIAL_MODELS),
    )
    _logger.info(
        "Migrated territorial XML IDs from %s to %s: %s moved, %s duplicate aliases removed",
        OLD_MODULE,
        NEW_MODULE,
        cr.rowcount,
        removed_aliases,
    )
