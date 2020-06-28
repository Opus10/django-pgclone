import contextlib
import io
import subprocess

from django.core.management import call_command

from . import database
from . import logging


def run_shell(cmd, ignore_errors=False):
    """
    Utility for running a command. Ensures that an error
    is raised if it fails.
    """
    logger = logging.get_logger()
    process = subprocess.Popen(
        cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    for line in iter(process.stdout.readline, b''):
        logger.info(line.decode('utf-8').rstrip())
    process.wait()

    if process.returncode and not ignore_errors:
        # Dont print the command since it might contain
        # sensitive information
        raise RuntimeError('Error running command.')

    return process


def run_management(cmd, *cmd_args, **cmd_kwargs):
    logger = logging.get_logger()
    cmd_args = cmd_args or []
    cmd_kwargs = cmd_kwargs or {}
    output = io.StringIO()
    try:
        with contextlib.redirect_stderr(output):
            with contextlib.redirect_stdout(output):
                call_command(cmd, *cmd_args, **cmd_kwargs)
    except Exception:  # pragma: no cover
        # If an exception happened, be sure to print off any stdout/stderr
        # leading up the error and log the exception.
        logger.info(output.getvalue())
        logger.exception(f'An exception occurred during "manage.py {cmd}"')
        raise
    else:
        logger.info(output.getvalue())


def run_psql(sql, *, db, ignore_errors=False):
    """Runs psql -c with properly formatted SQL"""
    db_url = database.get_url(db)

    # Format special SQL characters
    sql = (
        sql.replace('$', '\\$').replace('\n', ' ').replace('"', '\\"').strip()
    )
    return run_shell(
        f'psql {db_url} -P pager=off -c "{sql};"', ignore_errors=ignore_errors
    )
