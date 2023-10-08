# Storage Backends

The storage path and backend for `django-pgclone` is determined by `settings.PGCLONE_STORAGE_LOCATION`, which defaults to `.pgclone/`. This can be overridden in a [configuration](configurations.md).

## Using an S3 backend

S3 storage is enabled by configuring a path that starts with `s3://`. A bucket and optional prefix must be provided (e.g. `s3://my_bucket/prefix/path/`).

When using S3, dumps and restores are streamed, reducing the memory consumption required for large databases.

In order to use the S3 storage backend, one must additionally install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). Earlier versions of the CLI can be installed with `pip install awscli`.

!!! warning

    Installing the AWS CLI with pip can cause dependency issues in projects that depend on later versions of colorama or docutils. It is recommended to manually install the CLI using the [installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) if the pip version doesn't work.

## Configuring the S3 backend

The AWS CLI can be configured by environment variables. Inject custom environment variables by configuring `settings.PGCLONE_S3_CONFIG`. Here we override the AWS credentials and region:

```python

import os

PGCLONE_S3_CONFIG = {
    "AWS_ACCESS_KEY_ID": os.environ["PGCLONE_AWS_ACCESS_KEY_ID"],
    "AWS_SECRET_ACCESS_KEY": os.environ["PGCLONE_AWS_SECRET_ACCESS_KEY"],
    "AWS_DEFAULT_REGION": "us-east-1"
}
```

See [this guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) for all environment variables that can be used with the AWS CLI.

If using a non-standard AWS endpoint url or a non-AWS S3 provider, the endpoint url must be specified. Unfortunately, AWS CLI does not provide an environmental variable for this purpose. Instead, use the `settings.PGCLONE_S3_ENDPOINT_URL` setting, which will override the AWS CLI commands with the `--endpoint-url` option. `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` must still be specified in `settings.PGCLONE_S3_CONFIG`.

```python
PGCLONE_S3_ENDPOINT_URL = "https://endpoint.example.com"
```
