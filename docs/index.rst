django-pgclone
==============

``django-pgclone`` provides commands and utilities for doing Postgres dumps and
restores. In contrast with other Django database copy/restore apps
like `django-db-backup <https://github.com/django-dbbackup/django-dbbackup>`__,
``django-pgclone`` has the following advantages:

1. Defaults to streaming restores (when S3 is enabled) for larger databases
   and limited instance memory.
2. Provides hooks into the dump and restoration process, allowing users to
   perform migrations and other user-specified management commands
   *before* the restored database is swapped into the main one without
   interfering with the application.
3. Allows ``ls`` of database dumps and easily restoring the latest
   dump of a particular database.


Quickstart
----------

There are three main subcommands provided by the
``manage.py pgclone`` management command:

1. ``manage.py pgclone dump``: Dumps a compressed version of the
   instance's database to ``settings.PGCLONE_STORAGE_LOCATION``. The dump
   key is in the format ``{database_name}/{timestamp}.{config_name}.dump``
2. ``manage.py pgclone ls``: Lists all dumped database copies under
   ``settings.PGCLONE_STORAGE_LOCATION``. To list a single database, do
   ``manage.py pgclone ls <database_name>``. To list all available
   databases do ``manage.py pgclone ls --only-db-names``.
3. ``manage.py pgclone restore <dump_key or db_name>``: Restores the
   database. If a database name is provided, restores to the most recent
   snapshot of that database. Otherwise restores the provided dump key.

The ``PGCLONE_STORAGE_LOCATION`` setting determines where all of the database
dumps are stored. It defaults to the local ``.pgclone/`` directory. Using
an S3 path such as ``s3://mybucket/prefix`` will use
`boto <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`__
to store database dumps in S3.

``dump`` and ``restore`` have additional arguments for configuring hooks
and other parameters related to the underlying ``pg_dump`` and ``pg_restore``
commands that happen. These parameters can either be passed into the commands
as arguments or provided as settings in ``settings.py``.

The following is an example of a dump configuration that excludes various
models from being dumped::

    PGCLONE_DUMP_CONFIGS = {
        'default': {
            # Exclude the user table from being dumped.
            'exclude_models': ['auth.User']
        }
    }

When overriding the default configuration like so, performing
``manage.py pgclone dump`` will exclude the ``User`` table. One can
also run ``manage.py pgclone dump --exclude-model auth.User`` to achieve
the same thing.

Dump and Restore Hooks
----------------------

``django-pgclone`` allows one to hook into the dump or restore process
at a few specific points in time. To create a hook, create a management
command in your application and provide the management command name as
the hook.
``django-pgclone`` will run the management command against the appropriate
database at the following specific points in time:

1. pre-dump: A "pre-dump" hook is one that runs before the database dumping
   takes place. The hook runs on the default database being used. Users that
   write pre-dump hooks must remember that any modifications in the pre-dump
   hook *will* be applied to the current application database. We will
   show some examples of pre-dump hooks later.
2. pre-swap: A "pre-swap" hook is one that runs during restoration before
   the temporary database is swapped into the primary database. When running
   ``manage.py pgclone restore``, the ``pg_restore`` command happens behind
   the scenes on a temporary database. When the restore is complete, any
   pre-swap hooks are executed on the temporary database. The final swap
   happens when all hooks have successfully finished. Pre-swap hooks will
   automatically have their database commands executed on the temporary
   database using connection routing capabilities from
   `django-pgconnection <https://django-pgconnection.readthedocs.io>`__.
   By default, the ``migrate`` command is performed as a pre-swap hook
   during restore. Users can do
   ``manage.py pgclone restore --pre-swap-hook migrate --pre-swap-hook other_manage_command``
   to run pre-swap hooks or they can provide a ``PGCLONE_RESTORE_CONFIGS``
   setting.

Reversible and Local Restores
-----------------------------

``manage.py pgclone restore`` has a ``--reversible`` option that when used
will keep around a "previous" and a "current" copy of the database. The
"previous" copy will reference the database that existed *before* the restore
started. The "current" copy will reference the database that existed
right *after* the restore finished.

These two local copies can be reference with special syntax when restoring.
For example, ``manage.pg pgclone restore :current`` will restore back to the
state of the original database, and ``manage.pg pgclone restore :previous``
will revert back to the previous copy.

.. note::

    If one restores to ``:previous`` or ``:current`` and does not
    use the ``--reversible`` flag, they will no longer be able to
    use ``:previous`` or ``:current`` in later restores since these
    resources will be deleted.

The concept of ``:previous`` and ``:current`` restores extend to any
database that is locally present. In order to see the available local
database that can be used for restore, do ``manage.py pgclone ls --local``.

Dumping RDS Postgres Databases
------------------------------

RDS requires a preparatory step to take place in order to dump
the database. This can be handled by writing a pre-dump hook
management command like the following:


.. code-block:: python

  class Command(BaseCommand):
      def handle(self, *args, **options):
          print_msg(f'Running RDS prep SQL.')
          rds_prep_sql = '''
              CREATE OR REPLACE FUNCTION exec(text)
                  returns text language plpgsql volatile AS
                  $f$ BEGIN EXECUTE $1; RETURN $1; END; $f$;
              SELECT exec(
                  'ALTER TABLE ' || quote_ident(s.nspname)
                  || '.' || quote_ident(s.relname) || ' OWNER TO rds_superuser'
              )
              FROM (
                  SELECT nspname, relname
                  FROM pg_class c JOIN pg_namespace n ON (c.relnamespace = n.oid)
                  WHERE nspname in ('tiger','topology') AND
                  relkind IN ('r','S','v') ORDER BY relkind = 'S')
              s;
          '''
          with connection.cursor() as cursor:
              cursor.execute(rds_prep_sql)

After you write this management command, edit your
``settings.PGCLONE_DUMP_CONFIGS`` as follows::

    PGCLONE_DUMP_CONFIGS = {
        'default': {
            'pre_dump_hooks': 'rds_prep_management_command_name'
        }
    }

Disabling Restores in Production
--------------------------------
Set ``settings.PGCLONE_ALLOW_RESTORE`` to ``False`` as a secondary level of protection
against someone accidentally running a database restore on a production instance.
