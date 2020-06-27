import pytest

from pgclone import exceptions
from pgclone import settings as pgclone_settings


def test_validate(settings):
    """
    Verifies that settings are validated appropriately
    """
    settings.PGCLONE_DUMP_CONFIGS = {'default': {'exclude_models': []}}
    settings.PGCLONE_RESTORE_CONFIGS = {'default': {'pre_swap_hooks': []}}
    pgclone_settings.validate()

    # A default dump config must be defined
    settings.PGCLONE_DUMP_CONFIGS = {}
    with pytest.raises(exceptions.ConfigurationError):
        pgclone_settings.validate()
    settings.PGCLONE_DUMP_CONFIGS = {'default': {'exclude_models': []}}
    pgclone_settings.validate()

    # A default restore config must be defined
    settings.PGCLONE_RESTORE_CONFIGS = {}
    with pytest.raises(exceptions.ConfigurationError):
        pgclone_settings.validate()
    settings.PGCLONE_RESTORE_CONFIGS = {'default': {'pre_swap_hooks': []}}
    pgclone_settings.validate()
