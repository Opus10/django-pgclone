import contextlib
import io
import os
import subprocess

from django.core.management import call_command

from pgclone import exceptions, logging


def shell(cmd, ignore_errors=False, env=None):
    """
    Utility for running a command. Ensures that an error
    is raised if it fails.
    """
    env = env or {}
    logger = logging.get_logger()
    process = subprocess.Popen(
        cmd,
        shell=True,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
        env=dict(os.environ, **env),
    )
    for line in iter(process.stdout.readline, b""):
        logger.info(line.decode("utf-8").rstrip())
    process.wait()

    if process.returncode and not ignore_errors:
        # Dont print the command since it might contain
        # sensitive information
        raise exceptions.RuntimeError("Error running command.")

    return process


def management(cmd, *cmd_args, **cmd_kwargs):
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
