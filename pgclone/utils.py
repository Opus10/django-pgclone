import contextlib
import copy
import re
import threading

from django.db import connections, DEFAULT_DB_ALIAS
from django.db.utils import load_backend

from pgclone import logging


_routed_connection = threading.local()


def _route(execute, sql, params, many, context):
    """A hook that routes to the routed connection"""
    assert _routed_connection.value

    with _routed_connection.value.cursor() as cursor:
        context = copy.copy(context)
        context["connection"] = _routed_connection.value
        context["cursor"] = cursor

        return execute(sql, params, many, context)


@contextlib.contextmanager
def route(destination, using=DEFAULT_DB_ALIAS):
    """
    Route connections to another database.

    Args:
        destination (dict): Database configuration dictionary to be routed.
        using (str, default='default'): The source database to use when
            routing to another database. Defaults to the default database.
    """
    if not isinstance(destination, dict) or "ENGINE" not in destination:  # pragma: no cover
        raise ValueError(
            "Destination database must be a configuration dictionary in the"
            " same format as databases from settings.DATABASES."
        )

    _routed_connection.value = load_backend(destination["ENGINE"]).DatabaseWrapper(
        destination, using
    )

    with connections[using].execute_wrapper(_route):
        try:
            yield
        finally:
            _routed_connection.value.close()
            _routed_connection.value = None


def print_msg(msg):
    """
    Interface for printing a message to the user. Uses logging
    so that we can turn it off when not running in management
    commands.
    """
    logger = logging.get_logger()
    logger.info("\033[32m" + msg + "\033[0m")


def is_valid_dump_key(dump_key):
    """
    True if the `dump_key` is in the valid format of
    "database_name/timestamp.dump"
    """
    regexmatch = re.match(
        r"^[\w-]+/\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}_\d+\.\w+\.dump$",
        dump_key,
    )
    return regexmatch
