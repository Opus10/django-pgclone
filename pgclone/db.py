import contextlib
import copy
import functools
import threading

from django.conf import settings as django_settings
from django.db import connections
from django.db.utils import load_backend

from pgclone import exceptions, settings


_routed_connection = threading.local()


def _route(execute, sql, params, many, context):
    """A hook that routes to the routed connection"""
    cursor = context["cursor"]

    # Override the cursorwrapper's cursor with our own
    if cursor.db != _routed_connection.value:  # pragma: no branch
        cursor.cursor.close()
        cursor.cursor = _routed_connection.value.cursor()
        cursor.db = _routed_connection.value

    return execute(sql, params, many, context)


@contextlib.contextmanager
def route(destination):
    """
    Route all connections to another database.

    Args:
        destination (dict): Database configuration dictionary to be routed.
        using (str): The source database to use when
            routing to another database. Defaults to the default database.
    """
    _routed_connection.value = load_backend(destination["ENGINE"]).DatabaseWrapper(
        destination, "routed"
    )

    with contextlib.ExitStack() as stack:
        for alias in connections:
            stack.enter_context(connections[alias].execute_wrapper(_route))

        try:
            yield
        finally:
            _routed_connection.value.close()
            _routed_connection.value = None


def conf(*, using):
    """Obtain a copy of a database configuration"""
    if using not in django_settings.DATABASES:  # pragma: no cover
        raise exceptions.ValueError(
            f'"{using}" is not a valid database. Use one from settings.DATABASES.'
        )

    # Deep copy to ensure the caller doesn't modify this django setting
    return copy.deepcopy(django_settings.DATABASES[using])


def make(db_name, *, using):
    """Returns a DB config dict for the database named "db_name"

    Also ensures that no other database are configured with the provided
    database name. This is a sanity check to make sure that no dynamic
    databases used by pgclone collide with any that already exist.

    Note: In a multi-DB setup, this check might produce errors that don't
    need to happen, such as restricting one from using a name on an
    entirely different DB. We can handle this edge case later
    """
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
    return (
        f'postgresql://{db_config["USER"]}:{db_config["PASSWORD"]}'
        f'@{db_config["HOST"]}:{db_config["PORT"]}/{db_config["NAME"]}'
    )
