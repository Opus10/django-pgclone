from django.conf import settings

from . import exceptions


def get_storage_location():
    location = getattr(settings, 'PGCLONE_STORAGE_LOCATION', '.pgclone')
    if not location.endswith('/'):  # pragma: no cover
        location += '/'
    return location


def get_allow_restore():
    return getattr(settings, 'PGCLONE_ALLOW_RESTORE', True)


def get_dump_configs():
    return getattr(
        settings,
        'PGCLONE_DUMP_CONFIGS',
        {'default': {'exclude_models': [], 'pre_dump_hooks': []}},
    )


def get_restore_configs():
    return getattr(
        settings,
        'PGCLONE_RESTORE_CONFIGS',
        {'default': {'pre_swap_hooks': ['migrate']}},
    )


def validate():
    """Verify that pgclone settings are configured properly"""
    dump_configs = get_dump_configs()
    if not dump_configs.get('default'):
        raise exceptions.ConfigurationError(
            'You need to configure a default pgclone dump configuration'
            ' in settings.PGCLONE_DUMP_CONFIGS.'
            ' See the docs at https://django-pgclone.readthedocs.io for more'
            ' information.'
        )

    restore_configs = get_restore_configs()
    if not restore_configs.get('default'):
        raise exceptions.ConfigurationError(
            'You need to configure a default pgclone restore configuration'
            ' in settings.PGCLONE_RESTORE_CONFIGS.'
            ' See the docs at https://django-pgclone.readthedocs.io for more'
            ' information.'
        )
