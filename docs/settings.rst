.. _settings:

Settings
========

Below are all settings for ``django-pgclone``.

.. note::

    Most settings relate to command options and are global defaults for them.
    Check out the :ref:`basics` section for more information on how default
    values for commands are determined.

PGCLONE_ALLOW_RESTORE
---------------------

If ``False``, running any restore results in an error.

**Default** ``True``

PGCLONE_CONFIGS
---------------

Configurations that store options for the commands. For example:

.. code-block:: python

    PGCLONE_CONFIGS = {
        "no_users": {
            "exclude": ["auth.User"]
        }
    }

See the :ref:`configurations` section for more information on what
options can be configured.

**Default** ``{}``

PGCLONE_CONN_DB
---------------

The connection database used when running ``psql`` commands. A connection database that
is different from the dumped or restored database must be used for special commands
like killing connections before swapping restores.

**Default** ``postgres`` if there are no ``postgres`` databases in ``settings.DATABASES``,
otherwise ``template1`` is used.

PGCLONE_DATABASE
----------------

The default database to use for commands.

**Default** ``default``

PGCLONE_EXCLUDE
---------------

The tables to exclude for dumps.

**Default** ``[]``

PGCLONE_INSTANCE
----------------

The instance name to use in the dump key. For example,
using "prod" as the instance when running production dumps.

**Default** Uses ``socket.gethostname()`` to generate the instance.

PGCLONE_PRE_DUMP_HOOKS
----------------------

The hooks to run by default for dumps.

**Default** ``[]``

PGCLONE_PRE_SWAP_HOOKS
----------------------

The hooks to run by default for restores before swapping happens.

**Default** ``["migrate"]``

PGCLONE_REVERSIBLE
------------------

``True`` if the restore command should create reversible restores by default.
See the :ref:`reversible` section for more information.

**Default** ``False``

PGCLONE_S3_CONFIG
-----------------

The environment variable overrides when using the AWS CLI. Only applicable when
using the S3 storage backend.

For example:

.. code-block:: python

    PGCLONE_S3_CONFIG = {
        "AWS_ACCESS_KEY_ID": "acces_key",
        "AWS_SECRET_ACCESS_KEY": "secret_access_key_read_from_environment",
        "AWS_DEFAULT_REGION": "us-east-1"
    }

**Default**: ``{}``

PGCLONE_STORAGE_LOCATION
------------------------

Where dumps are stored. Use relative paths to store in the local
file system. Use paths that begin with ``s3://`` to use an S3 storage backend.
See :ref:`storage`.

For example:

.. code-block:: python

    PGCLONE_STORAGE_LOCATION = "s3://bucket/prefix/"

**Default** ``.pgclone/``

PGCLONE_VALIDATE_DUMP_KEYS
--------------------------

``False`` if invalid dump keys should be returned by ``python manage.py pgclone ls``.
This helps preserve backwards compatibility with version 1. Note that
``--instances``, ``--databases``, and ``--configs`` arguments will ignore invalid
keys.

**Default** ``True``
