import pytest

from pgclone import settings as pgclone_settings


def test_s3_config(settings):
    delattr(settings, "PGCLONE_S3_CONFIG")
    assert not pgclone_settings.s3_config()
    settings.PGCLONE_S3_CONFIG = {"AWS_ACCESS_KEY_ID": "access_key"}
    assert pgclone_settings.s3_config() == {"AWS_ACCESS_KEY_ID": "access_key"}


def test_conn_db(settings):
    delattr(settings, "PGCLONE_CONN_DB")
    settings.DATABASES = {"default": {"NAME": "hello"}}

    pgclone_settings.conn_db.cache_clear()
    assert pgclone_settings.conn_db() == "postgres"

    settings.DATABASES = {"default": {"NAME": "postgres"}}

    # Verify the cache works...
    assert pgclone_settings.conn_db() == "postgres"

    pgclone_settings.conn_db.cache_clear()
    assert pgclone_settings.conn_db() == "template1"

    settings.DATABASES = {"default": {"NAME": "postgres"}, "other": {"NAME": "template1"}}
    pgclone_settings.conn_db.cache_clear()
    with pytest.raises(RuntimeError):
        pgclone_settings.conn_db()

    settings.PGCLONE_CONN_DB = "other"
    pgclone_settings.conn_db.cache_clear()
    assert pgclone_settings.conn_db() == "other"
