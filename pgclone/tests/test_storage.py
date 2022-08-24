import pytest

from pgclone import storage


@pytest.fixture(autouse=True)
def dont_validate_s3_support(mocker):
    """None of our S3 tests use boto or awscli, so dont validate S3 support"""
    mocker.patch("pgclone.storage.validate_s3_support", autospec=True)


def test_s3_env(settings):
    settings.PGCLONE_S3_CONFIG = {
        "AWS_ACCESS_KEY_ID": "access_key",
        "AWS_SECRET_ACCESS_KEY": "secret_access_key",
        "AWS_DEFAULT_REGION": "region",
    }

    assert storage.S3("bucket").env == {
        "AWS_ACCESS_KEY_ID": "access_key",
        "AWS_SECRET_ACCESS_KEY": "secret_access_key",
        "AWS_DEFAULT_REGION": "region",
    }

    delattr(settings, "PGCLONE_S3_CONFIG")

    assert storage.S3("bucket").env == {}


def test_s3_pg_dump():
    assert storage.S3("bucket").pg_dump("file_path") == "| aws s3 cp - file_path"


def test_s3_pg_restore():
    assert storage.S3("bucket").pg_restore("file_path") == "aws s3 cp file_path - |"
