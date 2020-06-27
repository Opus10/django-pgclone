import re

from pgclone import logging


def print_msg(msg):
    """
    Interface for printing a message to the user. Uses logging
    so that we can turn it off when not running in management
    commands.
    """
    logger = logging.get_logger()
    logger.info('\033[32m' + msg + '\033[0m')


def is_valid_dump_key(dump_key):
    """
    True if the `dump_key` is in the valid format of
    "database_name/timestamp.dump"
    """
    regexmatch = re.match(
        r'^[\w-]+/\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}_\d+\.\w+\.dump$',
        dump_key,
    )
    return regexmatch
