import os

from django.db import connection
import pgconnection

from pgclone import command
from pgclone import database
from pgclone import exceptions
from pgclone import ls
from pgclone import settings
from pgclone.utils import is_valid_dump_key
from pgclone.utils import print_msg


def get_latest_dump_key(db_name):
    """
    Given a database name, lists all of the dumps and finds the most
    recent dump key.
    """
    sorted_dumps = sorted(ls(db_name=db_name))
    return sorted_dumps[-1] if sorted_dumps else None


def _db_exists(db):
    """Returns True if the database exists"""
    conn_db = database.make_config('postgres')
    db_url = database.get_url(conn_db)
    try:
        command.run_shell(
            f'psql {db_url} -lqt | cut -d \\| -f 1 | grep -qw {db["NAME"]}'
        )
        return True
    except RuntimeError:
        return False


def _make_restore_config(*, pre_swap_hooks=None):
    """Make a pgclone restore config"""
    return {'pre_swap_hooks': pre_swap_hooks or []}


def _get_restore_config(restore_config_name):
    """Get a pgclone restore config by its name"""
    if restore_config_name not in settings.get_restore_configs():
        raise exceptions.ConfigurationError(
            f'"{restore_config_name}" is not a valid restore configuration'
            ' in settings.PGCLONE_RESTORE_CONFIGS.'
        )

    return _make_restore_config(
        **settings.get_restore_configs()[restore_config_name]
    )


def _kill_connections_to_database(db):
    conn_db = database.make_config('postgres')

    kill_connections_sql = f'''
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db["NAME"]}'
            AND pid <> pg_backend_pid()
    '''
    command.run_psql(kill_connections_sql, db=conn_db)


def _drop_db(db):
    conn_db = database.make_config('postgres')
    _kill_connections_to_database(db)
    drop_sql = f'DROP DATABASE IF EXISTS "{db["NAME"]}"'
    command.run_psql(drop_sql, db=conn_db)


def _set_search_path(db, conn_db):
    """
    pg_restore does not restore the original search_path variable of the
    database, which can cause issues with extensions. This function obtains
    the original search path and sets it as the search path of the restored
    database

    https://www.postgresql.org/message-id/CAKFQuwbWpd1DXA_YY3zXRKGKKLL1ZTi9MHDQ15zJ8ufVBwVJEA%40mail.gmail.com
    """
    with connection.cursor() as cursor:
        cursor.execute('SHOW search_path;')
        search_path = cursor.fetchone()[0]

    set_search_path_sql = (
        f'ALTER DATABASE "{db["NAME"]}"' f' SET search_path to {search_path}'
    )
    command.run_psql(set_search_path_sql, db=conn_db)


def _local_restore(db_name_or_dump_key, *, conn_db, temp_db, curr_db, prev_db):
    """
    Performs a restore using a local database
    """
    if db_name_or_dump_key == ':current':
        local_restore_db = curr_db
    elif db_name_or_dump_key == ':previous':
        local_restore_db = prev_db
    else:
        local_restore_db = database.make_config(db_name_or_dump_key[1:])

    if not _db_exists(local_restore_db):
        raise RuntimeError(
            f'local database {local_restore_db["NAME"]} does not exist.'
            ' Use "pgclone ls --local" to see local database keys.'
        )

    # Perform the local restore process. It is completely valid to
    # try to restore the temp_db, so do nothing if this database
    # is provided by the user
    if local_restore_db != temp_db:  # pragma: no branch
        _drop_db(temp_db)
        create_temp_sql = f'''
            CREATE DATABASE {temp_db["NAME"]}
            TEMPLATE {local_restore_db["NAME"]}
        '''
        command.run_psql(create_temp_sql, db=conn_db)

    _set_search_path(temp_db, conn_db)

    return db_name_or_dump_key


def _remote_restore(db_name_or_dump_key, *, temp_db, conn_db):
    # We are restoring from a remote dump. If the dump key is not valid,
    # assume it is the latest dump of a database name and get the latest
    # dump key
    dump_key = db_name_or_dump_key
    if not is_valid_dump_key(dump_key):
        dump_key = get_latest_dump_key(db_name_or_dump_key)
        if not dump_key:
            raise RuntimeError(
                'Could not find a dump for database name'
                f' "{db_name_or_dump_key}"'
            )

    storage_location = settings.get_storage_location()
    file_path = os.path.join(storage_location, dump_key)

    print_msg(f'Creating the temporary restore db')
    _drop_db(temp_db)
    create_temp_sql = f'CREATE DATABASE "{temp_db["NAME"]}"'
    command.run_psql(create_temp_sql, db=conn_db)
    _set_search_path(temp_db, conn_db)

    print_msg(f'Running pg_restore on "{dump_key}"')
    pg_restore_cmd = (
        'pg_restore --verbose --no-acl --no-owner '
        f'-d \'{database.get_url(temp_db)}\''
    )

    # When restoring, we need to ignore errors because there are certain
    # errors we cannot get around when pg restoring some DBs (like Aurora).
    # In the future, we may parse the output of the pg_restore command to see
    # if an unexpected error happened.
    if storage_location.startswith('s3://'):  # pragma: no cover
        command.run_shell(
            f'aws s3 cp {file_path} - | {pg_restore_cmd}', ignore_errors=True
        )
    else:
        command.run_shell(f'{pg_restore_cmd} {file_path}', ignore_errors=True)

    return dump_key


def restore(
    db_name_or_dump_key,
    pre_swap_hooks=None,
    restore_config_name=None,
    reversible=False,
):
    """
    Restores a database dump

    Args:
        db_name_or_dump_key (str): When a database name
            is provided, finds the most recent dump for that
            database and restores it. Restores a specific dump
            when a dump key is provided.
        pre_swap_hooks (List[str], default=None): The list of pre_swap hooks to
            run before swapping the temp restore database with the
            main database. The strings are management command names.
        restore_config_name (str, default=None): The name of the restore
            config to use when running the restore. Configured
            in settings.PGCLONE_RESTORE_CONFIGS

    Returns:
        str: The dump key that was restored.
    """
    settings.validate()

    if not settings.get_allow_restore():  # pragma: no cover
        raise RuntimeError('Restore not allowed')

    if restore_config_name and pre_swap_hooks:  # pragma: no cover
        raise ValueError(
            'Cannot pass in pre_swap_hooks when using a restore config'
        )
    elif pre_swap_hooks:
        restore_config_name = '_custom'
        restore_config = _make_restore_config(pre_swap_hooks=pre_swap_hooks)
    else:
        restore_config_name = restore_config_name or 'default'
        restore_config = _get_restore_config(restore_config_name)

    # Restore works in the following steps with the following databases:
    # 1. Create the temp_db database to perform the restore without
    #    affecting the default_db
    # 2. Call pg_restore on temp_db
    # 3. Apply any pre_swap_hooks to temp_db
    # 4. Terminate all connections on default_db so that we
    #    can swap in the temp_db
    # 4. Rename default_db to prev_db
    # 5. Rename temp_db to default_db
    # 6. Delete prev_db
    #
    # Database variable names below reflect this process. We use the
    # "postgres" database (i.e. conn_db) as the connection database
    # when using psql for most of these commands

    default_db = database.get_default_config()
    temp_db = database.make_config(default_db['NAME'] + '__temp')
    prev_db = database.make_config(default_db['NAME'] + '__prev')
    curr_db = database.make_config(default_db['NAME'] + '__curr')
    conn_db = database.make_config('postgres')
    local_restore_db = None

    if db_name_or_dump_key.startswith(':'):
        dump_key = _local_restore(
            db_name_or_dump_key,
            conn_db=conn_db,
            temp_db=temp_db,
            curr_db=curr_db,
            prev_db=prev_db,
        )
    else:
        dump_key = _remote_restore(
            db_name_or_dump_key, temp_db=temp_db, conn_db=conn_db
        )

    # When in reversible mode, make a special __curr db snapshot.
    # Avoid this if we are restoring the current db
    if reversible and local_restore_db != curr_db:
        print_msg('Creating snapshot for reversible restore')
        _drop_db(curr_db)
        create_current_db_sql = f'''
            CREATE DATABASE "{curr_db['NAME']}"
             WITH TEMPLATE
            "{temp_db['NAME']}"
        '''
        command.run_psql(create_current_db_sql, db=conn_db)

    # pre-swap hook step
    with pgconnection.route(temp_db):
        for management_command_name in restore_config['pre_swap_hooks']:
            print_msg(
                f'Running "manage.py {management_command_name}" pre_swap hook'
            )
            command.run_management(management_command_name)

    # swap step
    print_msg('Swapping the restored copy with the primary database')
    _drop_db(prev_db)
    _kill_connections_to_database(default_db)
    alter_db_sql = f'''
        ALTER DATABASE "{default_db['NAME']}" RENAME TO
        "{prev_db['NAME']}"
    '''
    # There's a scenario where the default DB may not exist before running
    # this, so just ignore errors on this command
    command.run_psql(alter_db_sql, db=conn_db, ignore_errors=True)

    rename_sql = f'''
        ALTER DATABASE "{temp_db["NAME"]}"
        RENAME TO "{default_db["NAME"]}"
    '''
    command.run_psql(rename_sql, db=conn_db)

    if not reversible:
        print_msg('Cleaning old pgclone resources')
        _drop_db(curr_db)
        _drop_db(prev_db)

    print_msg(f'Successfully restored dump "{dump_key}"')

    return dump_key
