"""Reset noupdate flag on form templates before upgrade.

This allows the module upgrade to re-import template HTML with
updated placeholders (90/92 forms now have placeholders).
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
        'legal_forms pre-migrate 1.3.0: reset noupdate on %d template records',
        cr.rowcount,
    )
