import copy

from django.conf import settings


def get_default_config():
    # Deep copy to ensure the caller doesn't modify this django setting
    return copy.deepcopy(settings.DATABASES['default'])


def make_config(db_name):
    """Returns a DB config dict for the database named "db_name"

    Also ensures that no other database are configured with the provided
    database name. This is a sanity check to make sure that no dynamic
    databases used by pgclone collide with any that already exist.
    """
    for db in settings.DATABASES.values():
        if db.get('NAME') == db_name:  # pragma: no cover
            raise RuntimeError(
                f'pgclone cannot use temporary database named "{db_name}"'
                ' since it is already configured in settings.DATABASES.'
            )

    db_config = get_default_config()
    db_config['NAME'] = db_name
    return db_config


def get_url(db_config):
    """Convert a database dictionary config to a url"""
    return (
        f'postgresql://{db_config["USER"]}:{db_config["PASSWORD"]}'
        f'@{db_config["HOST"]}:{db_config["PORT"]}/{db_config["NAME"]}'
    )
