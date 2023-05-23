import contextlib
import copy
import functools
import shlex

from django.conf import settings as django_settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.utils import load_backend

from pgclone import exceptions, run, settings


def _no_queries_during_routing(execute, sql, params, many, context):  # pragma: no cover
    alias = context["connection"].alias
    raise RuntimeError(f'Cannot query non-default database "{alias}" during pgclone hooks')


@contextlib.contextmanager
def route(destination):
    """
    Route all connections to another database.

    Args:
        destination (dict): Database configuration dictionary to be routed.
        using (str): The source database to use when
            routing to another database. Defaults to the default database.
    """
    with contextlib.ExitStack() as stack:
        # Protect every connection from being queried
        for alias in connections:
            stack.enter_context(connections[alias].execute_wrapper(_no_queries_during_routing))

        # Swap the default and routed connection. Note: the connections object is thread safe
        default_connection = connections[DEFAULT_DB_ALIAS]
        connections[DEFAULT_DB_ALIAS] = load_backend(destination["ENGINE"]).DatabaseWrapper(
            destination, DEFAULT_DB_ALIAS
        )

        try:
            yield
        finally:
            connections[DEFAULT_DB_ALIAS].close()
            connections[DEFAULT_DB_ALIAS] = default_connection


def conf(*, using):
    """Obtain a copy of a database configuration"""
    if using not in django_settings.DATABASES:  # pragma: no cover
        raise exceptions.ValueError(
            f'"{using}" is not a valid database. Use one from settings.DATABASES.'
        )

    # Deep copy to ensure the caller doesn't modify this django setting
    database = copy.deepcopy(django_settings.DATABASES[using])

    # Set the same defaults as Django so that it works with routing. This
    # is copied directly from
    # https://github.com/django/django/blob/c8eb9a7c451f7935a9eaafbb195acf2aa9fa867d/django/db/utils.py#L160
    database.setdefault("ATOMIC_REQUESTS", False)
    database.setdefault("AUTOCOMMIT", True)
    database.setdefault("ENGINE", "django.db.backends.dummy")
    if database["ENGINE"] == "django.db.backends." or not database["ENGINE"]:  # pragma: no cover
        database["ENGINE"] = "django.db.backends.dummy"

    database.setdefault("CONN_MAX_AGE", 0)
    database.setdefault("OPTIONS", {})
    database.setdefault("TIME_ZONE", None)
    for setting in ["NAME", "USER", "PASSWORD", "HOST", "PORT"]:
        database.setdefault(setting, "")

    return database


def make(db_name, *, using, check=True):
    """Returns a DB config dict for the database named "db_name"

    Also ensures that no other database are configured with the provided
    database name. This is a sanity check to make sure that no dynamic
    databases used by pgclone collide with any that already exist.

    Note: In a multi-DB setup, this check might produce errors that don't
    need to happen, such as restricting one from using a name on an
    entirely different DB. We can handle this edge case later
    """
    if check:
        for db in django_settings.DATABASES.values():
            if db.get("NAME") == db_name:  # pragma: no cover
                raise exceptions.RuntimeError(
                    f'pgclone cannot use temporary database named "{db_name}"'
                    " since it is already configured in settings.DATABASES."
                )

    db_config = conf(using=using)
    db_config["NAME"] = db_name
    return db_config


@functools.lru_cache()
def conn(*, using):
    """Return the database used when making connections to psql"""
    return make(settings.conn_db(), using=using)


def url(db_config):
    """Convert a database dictionary config to a url"""
    return shlex.quote(
        f'postgresql://{db_config["USER"]}:{db_config["PASSWORD"]}'
        f'@{db_config["HOST"]}:{db_config["PORT"]}/{db_config["NAME"]}'
    )


def psql(sql, *, using, ignore_errors=False):
    """Runs psql -c with properly formatted SQL"""
    db_url = url(conn(using=using))

    # Format special SQL characters
    sql = sql.replace("$", "\\$").replace("\n", " ").replace('"', '\\"').strip()
    return run.shell(f'psql {db_url} -P pager=off -c "{sql};"', ignore_errors=ignore_errors)


def kill_connections(database, *, using):
    kill_connections_sql = f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{database["NAME"]}'
            AND pid <> pg_backend_pid()
    """
    psql(kill_connections_sql, using=using)


def drop(database, *, using):
    kill_connections(database, using=using)
    drop_sql = f'DROP DATABASE IF EXISTS "{database["NAME"]}"'
    psql(drop_sql, using=using)
