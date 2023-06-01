import pytest

from pgclone import db


@pytest.mark.parametrize(
    "lock_timeout, statement_timeout, sql, expected_sql",
    [
        (None, None, "COMMAND", "COMMAND;"),
        (1, None, " COMMAND; ", "SET lock_timeout = 1;\nCOMMAND;"),
        (1, 2, " COMMAND; ", "SET lock_timeout = 1;\nSET statement_timeout = 2;\nCOMMAND;"),
        (None, 2, " COMMAND; ", "SET statement_timeout = 2;\nCOMMAND;"),
        (
            None,
            None,
            "    COMMAND\n      INDENTED\n      INDENTED; ",
            "COMMAND\n  INDENTED\n  INDENTED;",
        ),
    ],
)
def test_fmt_psql_sql(settings, lock_timeout, statement_timeout, sql, expected_sql):
    """Tests variations of the db._fmt_psql_sql command"""
    settings.PGCLONE_STATEMENT_TIMEOUT = statement_timeout
    settings.PGCLONE_LOCK_TIMEOUT = lock_timeout
    assert db._fmt_psql_sql(sql) == expected_sql
