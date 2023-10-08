# Basics

Here we cover some of the basics of `django-pgclone` to make it easier to understand the docs and the tool.

## Core features

`django-pgclone` has four primary commands:

1. `python manage.py pgclone ls`: Lists dumps.
2. `python manage.py pgclone dump`: Dump a database.
3. `python manage.py pgclone restore`: Restore a database.
4. `python manage.py pgclone copy`: Make a local copy of a database.

The `dump` and `restore` commands wrap [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html) and [pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html). Dumps and restores are compressed and streamed to and from a storage location. File names are visible with the `ls` command.

`restore` can restore local databases, such as local copies created during `pgclone restore --reversible` or with `pgclone copy`.

Users can write [Hooks](hooks.md) for dumping and restoring. For example:

1. Writing a pre-dump hook that disables dumping if the data isn't anonmymized.
2. Writing a pre-restore hook that does migrations or any additional data prep for a functioning application.

Restoration works behind the scenes on a temporary database without interfering with the running app. Once the database has been successfully restored and hooks have successfully executed, connections to the primary database are killed and the restored database is swapped in.

Users can use [Reversible Restores](reversible.md) to keep old copies of the database around to quickly revert changes. This process allows for several flows:

1. Testing complex data migrations.
2. Testing application flows (e.g. onboarding) multiple times from a clean slate.
3. Reverting a production deployment when migrations aren't reversible.

Options for dump, restore, and ls can be stored in [Configurations](configurations.md) for re-use and for defining different flows. For example, one can make a configuration for dumping and restoring anonymous production databases that uses a different storage location than the default.

## Dump keys

When dumping databases, `django-pgclone` stores dumps that are referenced by a "dump key" under the configured storage location. Dump keys can be listed with `python manage.py pgclone ls` and supplied to `python manage.py pgclone restore`.

Dump keys are in the format of `<instance>/<database>/<config>/<timestamp>.dump`. The parts have the following meaning:

* **instance**: The database instance. By default, the `hostname` of the dump command is used. Override this in [Configurations](configurations.md) or in [Settings](settings.md) to better label the instance of the database. For example, using `prod` as the instance for the production database.
* **database**: The database. This is the alias of the database from `settings.DATABASES`.
* **config**: The config used to create the dump or "none" if a config wasn't used. See [Configurations](configurations.md) for more information on configurations.
* **timestamp**: The time at which the dump happened.

Local database copies have a special dump key prefixed with the `:` symbol. These can be listed with `pgclone ls --local` and passed as the dump key to `pgclone restore`.

## Default values for command options

Default values for command options are determined in the following way:

1. If the option isn't provided, it is looked up in an optional [configuration](configurations.md) supplied to `-c` (or `--config`). Almost every option can be specified in a configuration, but [check the docs](configurations.md) to be sure.
2. If the option isn't in a config, use the value from [Settings](settings.md).

Given this hierarchy, keep in mind that any settings are global unless a config or direct user input overrides it.