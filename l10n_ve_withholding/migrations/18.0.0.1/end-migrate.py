# -*- coding: utf-8 -*-
"""Purga las traducciones de print_report_name que nombran campos de 15.

Por que en 'end' y no en 'post'
-------------------------------
print_report_name es un Char traducible, o sea un jsonb con un valor por
idioma. Al actualizar el modulo, Odoo reescribe el termino fuente (en_US) desde
el XML y no toca los demas idiomas, que es lo correcto para prosa y justo lo
contrario de lo que hace falta cuando el valor es codigo: en una base venida de
15 el es_VE se queda apuntando a withholding_number, campo que en 18 se llama
name y ademas vive en otro modelo. Como la sesion esta en es_VE, imprimir muere
en safe_eval.

El primer intento hizo esto mismo en post-migrate y casaba cero filas. El orden
de load_module_graph es load_data -> migrate_module(post) -> _update_translations,
pero load_data escribe por el ORM y sus valores no habian llegado a la base
cuando el cursor crudo de la migracion miro: para el, en_US seguia siendo el de
15, y la condicion que exigia un en_US ya limpio no se cumplia nunca.

En 'end' las dos cosas estan resueltas -- migrate_module(end) corre cuando ya se
proceso todo modulo, despues del volcado y despues de _update_translations -- y
ademas se quita esa condicion: se descarta cualquier idioma cuyo valor nombre
withholding_number, sea cual sea, en vez de fiarse de que otro este limpio.

Si no quedara ningun idioma el campo se queda vacio, que es inofensivo: Odoo
nombra el PDF con el nombre del informe. Lo que no puede es quedarse con codigo
que no evalua.
"""
import logging

_logger = logging.getLogger(__name__)

DEAD_FIELD = '%withholding_number%'


def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """
        UPDATE ir_act_report_xml
           SET print_report_name = COALESCE(
                   (SELECT jsonb_object_agg(lang, term)
                      FROM jsonb_each(print_report_name) AS translation(lang, term)
                     WHERE term::text NOT LIKE %s),
                   '{}'::jsonb)
         WHERE print_report_name::text LIKE %s
        """,
        (DEAD_FIELD, DEAD_FIELD),
    )
    if cr.rowcount:
        _logger.info(
            "Dropped stale print_report_name translations naming "
            "withholding_number: %s report(s)", cr.rowcount)
