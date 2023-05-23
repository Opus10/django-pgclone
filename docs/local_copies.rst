.. _local_copies:

Local Copies
============

Some database dump and restore flows can be facilitated by making local copies
so that they can be quickly restored later (as opposed to a full restore with
``pg_restore``). This can be accomplished with the ``pgclone copy`` command.

The ``pgclone copy`` command will copy the current database to a target database
name using ``CREATE DATABASE <source> TEMPLATE <target>``. By default, it uses
the same database name that ``pgclone restore --reversible`` uses when creating
the restore point of the current database.

In other words, you can do the following to create a copy of the database locally::

    python manage.py pgclone copy

And then you can restore it with the following::

    python manage.py pgclone restore :current

.. tip::

    By default, ``pgclone restore`` will delete the special ``:current`` database
    unless ``--reversible`` is supplied. Use a custom copy name as shown below to
    avoid this.

To create named local copies, pass in a key that begins with ``:``. For example::

    python manage.py pgclone copy :my_backup

You can later restore this backup with::

    python manage.py pgclone restore :my_backup

.. danger::

    Calling ``pgclone copy`` will take out an exclusive access lock on the default
    database when copying it, preventing all activity until the copy is done. Use
    with caution, especially when running this in a production environment.