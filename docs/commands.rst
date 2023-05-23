.. _commands:

Commands
========

``django-pgclone`` comes with the ``python manage.py pgclone`` command,
which has several subcommands that are described below.

.. tip::

    Keep in mind that most of the command line options have default values
    from :ref:`Configurations <configurations>` or :ref:`Settings <settings>`.
    Read the :ref:`basics` section for more information on how default
    values are determined.

ls
--

List all dumps under the storage location.

**Options**

dump_key
    A dump key or prefix of a dump key.

--instances  Only list the instances of the dump keys.
--databases  Only list the databases of the dump keys.
--configs  Only list the configs of the dump keys.
--local  Show all local databases that can be restored.
-d, --database  Use this database when listing local databases.
-s, --storage-location  Use this storage location for listing.
-c, --config  Use this configuration to supply default option values.

.. note::

    ``--instances``, ``--databases``, ``--configs``, and ``--local`` are
    mutually exclusive. 

dump
----

Dump the database. Dump names are in the format of ``<instance>/<database>/<config>/<timestamp>.dump``.

**Options**

-e, --exclude  Exclude a model from being dumped. Provide the full model name as
               ``<app_label>.<model_name>``. Can be used multiple times.
--pre-dump-hook  Execute a management command before the dump happens. Can be used
                 multiple times.
-i, --instance  Use this instance name in the dump key.
-d, --database  Dump this database.
-s, --storage-location  Dump to this storage location.
-c, --config  Use this configuration to supply default option values.

.. note::

    When doing a dump with ``-e`` or ``--pre-dump-hook`` and ``-c``, a config name of "none" will be
    used in the dump key since these parameters can alter the dump.

.. tip::

    Set ``settings.PGCLONE_ALLOW_DUMP`` to ``False`` to disable dumps.

restore
-------

Restore the database. Restores happen in a temporary database that is swapped into the main one
upon completion.

**Options**

dump_key
    A dump key or prefix of a dump key. If a prefix is provided, the most recent
    dump key matching it will be used. A dump key with ``:`` at the beginning
    means that we are restoring a local database, such as one created when restoring
    with the ``--reversible`` option.

--pre-swap-hook  Execute a management command on the restored database
                 before it is swapped to the primary. Can be used multiple times.
-r, --reversible  Keep current and previous database copies available for reversion.
-d, --database  Restore to this database.
-s, --storage-location  Restore from this storage location.
-c, --config  Use this configuration to supply default option values.

.. tip::

    Set ``settings.PGCLONE_ALLOW_RESTORE`` to ``False`` to disable restores.

copy
----

Make a local copy of the database using ``CREATE DATABASE <target> TEMPLATE <source>``.
By default, the default database is copied to the same name created when
performing a reversible restore, meaning one can do ``pgclone copy`` followed by
``pgclone restore :current`` to restore it.

**Options**

dump_key
    A dump key to identify the local copy. Must start with ``:`` and only consist
    of valid database name characters.

-d, --database  Copy this database.
-c, --config  Use this configuration to supply default option values.

.. danger::

    Running ``pgclone copy`` will take out an exclusive access lock on the source database,
    meaning all reads and writes to the database will be blocked until the operation
    is finished. Only use this command in non-production environments for fast
    copying and restores.

.. tip::

    Set ``settings.PGCLONE_ALLOW_COPY`` to ``False`` to disable copies.