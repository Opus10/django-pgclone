import os
import subprocess

import boto3

from pgclone import database
from pgclone import settings
from pgclone.utils import is_valid_dump_key


def _get_relative_path(storage_location, path):
    """
    Given a storage location and an absolute path, return
    the relative path (i.e. the dump key)
    """
    prefix_len = len(storage_location)
    return path[prefix_len:]


def ls(db_name=None, only_db_names=False, local=False):
    """
    Lists dump keys.

    Args:
        db_name (str, default=None): List dump keys only
            for this database name
        only_db_names (boolean, default=False): Lists only
            the unique database names associated with the dump
            keys
        local (bool, default=False): Only list local restore keys.

    Returns:
        List[str]: The list of dump keys (or database names).
    """
    settings.validate()
    storage_location = settings.get_storage_location()
    conn_db_url = database.get_url(database.make_config('postgres'))

    if local:
        cmd = f'psql {conn_db_url} -lqt | cut -d \\| -f 1'
        stdout = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE
        ).stdout.decode()

        return [
            f':{db_name.strip()}'
            for db_name in stdout.split('\n')
            if db_name.strip()
        ]

    if storage_location.startswith('s3://'):  # pragma: no cover
        bucket_name, prefix = storage_location[5:].split('/', 2)
        bucket = boto3.resource('s3').Bucket(bucket_name)

        abs_paths = [
            f's3://{obj.bucket_name}/{obj.key}'
            for obj in bucket.objects.filter(Prefix=prefix)
            if not obj.key.endswith('/')
        ]
    else:
        abs_paths = [
            os.path.join(dirpath, file_name)
            for dirpath, _, file_names in os.walk(storage_location)
            for file_name in file_names
        ]

    # Return paths relative to the storage location
    dump_keys = [
        _get_relative_path(storage_location, path)
        for path in abs_paths
        if is_valid_dump_key(_get_relative_path(storage_location, path))
    ]
    if db_name:
        dump_keys = [
            dump_key
            for dump_key in dump_keys
            if dump_key.startswith(f'{db_name}/')
        ]

    if only_db_names:
        return sorted(
            list({dump_key.split('/', 1)[0] for dump_key in dump_keys})
        )
    else:
        return sorted(dump_keys, reverse=True)
