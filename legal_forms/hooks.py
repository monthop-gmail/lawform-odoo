"""Module hooks for legal_forms."""
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Called after first install — reset noupdate so templates load."""
    env.cr.execute("""
        UPDATE ir_model_data
        SET noupdate = false
        WHERE module = 'legal_forms'
          AND model = 'legal.form.template'
    """)
    _logger.info(
        'legal_forms post_init: reset noupdate on %d template records',
        env.cr.rowcount,
    )
