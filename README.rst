django-pgclone
##############

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

Read the `docs <https://django-pgclone.readthedocs.io>`__ to get started
using the core management commands and to learn about how to configure
``django-pgclone`` for your use case.

Documentation
=============

`View the django-pgclone docs here
<https://django-pgclone.readthedocs.io/>`_.

Installation
============

Install django-pgclone with::

    pip3 install django-pgclone

After this, add ``pgclone`` to the ``INSTALLED_APPS``
setting of your Django project.

``django-pgclone`` depends on ``django-pgconnection``. Although
this dependency is automatically installed, one must add ``pgconnection``
to ``settings.INSTALLED_APPS`` and also configure the
``settings.DATABASES`` setting like so::

    import pgconnection

    DATABASES = pgconnection.configure({
        'default': # normal database config goes here...
    })

Contributing Guide
==================

For information on setting up django-pgclone for development and
contributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.

Primary Authors
===============

- @wesleykendall (Wes Kendall)
- @ethanpobrien (Ethan O'Brien)
