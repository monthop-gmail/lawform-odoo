"""Reset noupdate flag on form templates before upgrade.

This allows the module upgrade to re-import template HTML with
updated placeholders. Without this, Odoo skips noupdate=1 records.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        UPDATE ir_model_data
        SET noupdate = false
        WHERE module = 'legal_forms'
          AND model = 'legal.form.template'
    """)
    _logger.info(
        'legal_forms pre-migrate: reset noupdate on %d template records',
        cr.rowcount,
    )
