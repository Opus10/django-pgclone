import datetime as dt
import os
import pathlib

from django.apps import apps

from . import command
from . import database
from . import exceptions
from . import settings
from .utils import print_msg

DT_FORMAT = '%Y_%m_%d_%H_%M_%S_%f'


def _make_dump_config(*, exclude_models=None, pre_dump_hooks=None):
    """Make a pgclone dump config"""
    return {
        'exclude_models': exclude_models or [],
        'pre_dump_hooks': pre_dump_hooks or [],
    }


def _get_dump_config(dump_config_name):
    """Get a pgclone dump config by its name"""
    if dump_config_name not in settings.get_dump_configs():
        raise exceptions.ConfigurationError(
            f'"{dump_config_name}" is not a valid dump configuration'
            ' in settings.PGCLONE_DUMP_CONFIGS.'
        )

    return _make_dump_config(**settings.get_dump_configs()[dump_config_name])


def _get_dump_key(dump_config_name):
    """Obtain the key for the db dump"""
    now = dt.datetime.utcnow()
    file_name = f'{now.strftime(DT_FORMAT)}.{dump_config_name}.dump'
    return os.path.join(database.get_default_config()['NAME'], file_name)


def dump(exclude_models=None, dump_config_name=None, pre_dump_hooks=None):
    """Dumps a database copy

    Output location for the dump is determined by
    ``settings.PGCLONE_STORAGE_LOCATION``

    Args:
        exclude_models (List[str], default=None): The models to exclude when
            dumping the database.
        dump_config_name (str, default=None): The dump configuration name
            from ``settings.PGCLONE_DUMP_CONFIGS``. Defaults to ``default``
        pre_dump_hooks (List[str], default=None): A list of management
            command names to run before dumping the database.

    Returns:
        str: The dump key associated with the database dump.
    """
    settings.validate()
    default_db = database.get_default_config()

    if dump_config_name and (exclude_models or pre_dump_hooks):
        raise ValueError(
            'Cannot pass in exclude_models or pre_dump_hooks when using a'
            ' dump config'
        )
    elif exclude_models or pre_dump_hooks:
        dump_config_name = '_custom'
        dump_config = _make_dump_config(
            exclude_models=exclude_models, pre_dump_hooks=pre_dump_hooks
        )
    else:
        dump_config_name = dump_config_name or 'default'
        dump_config = _get_dump_config(dump_config_name)

    # pre-dump hooks
    for management_command_name in dump_config[
        'pre_dump_hooks'
    ]:  # pragma: no cover
        print_msg(
            f'Running "manage.py {management_command_name}" pre_dump hook'
        )
        command.run_management(management_command_name)

    # Run the pg dump command that streams to the storage location
    storage_location = settings.get_storage_location()
    dump_key = _get_dump_key(dump_config_name=dump_config_name)
    file_path = os.path.join(storage_location, dump_key)

    exclude_models = dump_config.get('exclude_models', [])
    exclude_tables = [
        apps.get_model(model)._meta.db_table for model in exclude_models
    ]
    exclude_args = ' '.join(
        [f'--exclude-table-data={table_name}' for table_name in exclude_tables]
    )
    # Note - do note format {db_dump_url} with an `f` string.
    # It will be formatted later when running the command
    pg_dump_cmd_fmt = (
        'pg_dump -Fc --no-acl --no-owner {db_dump_url} ' + exclude_args
    )

    if file_path.startswith('s3://'):  # pragma: no cover
        pg_dump_cmd_fmt += f' | aws s3 cp - {file_path}'
    else:
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        pg_dump_cmd_fmt += f' > {file_path}'

    anon_pg_dump_cmd = pg_dump_cmd_fmt.format(db_dump_url='<DB_URL>')
    print_msg(f'Creating DB copy with cmd: {anon_pg_dump_cmd}')

    pg_dump_cmd = pg_dump_cmd_fmt.format(
        db_dump_url=database.get_url(default_db)
    )
    command.run_shell(pg_dump_cmd)

    print_msg(f'DB successfully dumped to "{dump_key}"')

    return dump_key
