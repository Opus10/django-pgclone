django-pgclone
==============

``django-pgclone`` makes it easy to dump and restore Postgres databases.
Here are some key features:

1. Streaming dumps and restores to configurable storage backends like S3.
   Instances with limited memory aren't a problem for large databases.

2. A restoration process that works behind the scenes, swapping in
   the restored database when finished.

3. Configurable hooks into the dump and restore process, for example,
   migrating a restored database before it is swapped.

4. Reversible restores, making it possible to quickly revert to the initial
   restore or the previous database.

5. Re-usable configurations for instrumenting different types of dumps and restores.

Quickstart
----------

To dump a database, do::

    python manage.py pgclone dump

To list database dump keys, do::

    python manage.py pgclone ls

To restore a datase, do::

    python manage.py pgclone restore <dump_key>

Database dumps are relative to the storage location, which defaults to
the local file system. Dump keys are in
the format of ``<instance>/<database>/<config>/<timestamp>.dump``.

When listing, use an optional prefix. Restoring
supports the same interface, using the latest key that matches the
prefix.

Next steps
----------

``django-pgclone`` can be used in a number of ways. See the
following sections for more information:

* :ref:`basics` - A basic overview of the app, terminology, and
  how default command options are determined.
* :ref:`commands` - Documentation for commands and their options.
* :ref:`storage` - Configure an S3 storage backend.
* :ref:`hooks` - Run management command hooks during
  dumping or restoring.
* :ref:`reversible` - Create restores that can be quickly reverted.
* :ref:`configurations` - For re-using command parameters.
* :ref:`settings` - All settings.
* :ref:`rds` - Additional notes on Amazon RDS configuration.

See the :ref:`faq` for everything else.
