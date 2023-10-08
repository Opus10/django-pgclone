# Commands

`django-pgclone` comes with the `python manage.py pgclone` command, which has several subcommands that are described below.

!!! tip

    Keep in mind that most of the command line options have default values from [Configurations](configurations.md) or [Settings](settings.md). Read the [basics](basics.md) section for more information on how default values are determined.

## ls

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

!!! note

    `--instances`, `--databases`, `--configs`, and `--local` are mutually exclusive. 

## dump

Dump the database. Dump names are in the format of `<instance>/<database>/<config>/<timestamp>.dump`.

**Options**

    -e, --exclude  Exclude a model from being dumped. Provide the full model name as
                   `<app_label>.<model_name>`. Can be used multiple times.
    --pre-dump-hook  Execute a management command before the dump happens. Can be
                     used multiple times.
    -i, --instance  Use this instance name in the dump key.
    -d, --database  Dump this database.
    -s, --storage-location  Dump to this storage location.
    -c, --config  Use this configuration to supply default option values.

!!! note

    When doing a dump with `-e` or `--pre-dump-hook` and `-c`, a config name of "none" will be used in the dump key since these parameters can alter the dump.

!!! tip

    Set `settings.PGCLONE_ALLOW_DUMP` to `False` to disable dumps.

## restore

Restore the database. Restores happen in a temporary database that is swapped into the main one upon completion after hooks have finished. One can restore both dumps or local databases created via `pgclone copy` or as a result of using the `--reversible` option.

Reversible restores keep around copies of the database before and after the dump was restored. You can quickly revert to these copies with `pgclone restore :pre` or `pgclone restore :post`. Read more about reversible restores [here](reversible.md).

**Options**

    dump_key
        A dump key or prefix of a dump key. If a prefix is provided, the most recent
        dump key matching it will be used. A dump key with `:` at the beginning
        means that we are restoring a local database, such as one created when
        restoring with the `--reversible` option.

    --pre-swap-hook  Execute a management command on the restored database
                     before it is swapped to the primary. Can be used multiple
                     times.
    -r, --reversible  Keep local copies of before and after the restore happened.
                      This only applies to restoring dumps and has no effect when
                      restoring local copies.
    -d, --database  Restore to this database.
    -s, --storage-location  Restore from this storage location.
    -c, --config  Use this configuration to supply default option values.

!!! tip

    Set `settings.PGCLONE_ALLOW_RESTORE` to `False` to disable restores.

## copy

Make a local copy of the database using `CREATE DATABASE <target> TEMPLATE <source>`. For example, `pgclone copy :my_backup` makes a copy that can be restored with `pgclone restore :my_backup`.

**Options**

    dump_key
        The target database in the format of a local dump key. In other words, the
        local database name prefixed with `:`. The reserved names for reversible
        restores (`:pre` and `:post`) cannot be used.

    -d, --database  Copy this database.
    -c, --config  Use this configuration to supply default option values.

!!! danger

    Running `pgclone copy` will take out an exclusive access lock on the source database, meaning all reads and writes to the database will be blocked until the operation is finished. Only use this command in non-production environments for fast copying and restores.

!!! tip

    Set `settings.PGCLONE_ALLOW_COPY` to `False` to disable copies.