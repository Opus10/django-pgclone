.. _reversible:

Reversible Restores
===================

The ``--reversible`` option of ``manage.py pgclone restore`` keeps
the copy of the database after the restore (i.e. the "current" database)
and the copy of the database before the restore (i.e. the "previous" database).

The current database can be restored with::

    python manage.py pgclone restore :current

The previous database can be restored with::

    python manage.py pgclone restore :previous

Keep the following in mind when using ``--reversible``:

1. Restores take longer because an additional copy is made.
2. If you restore ``:current``, ``--reversible``
   must be used if you want to restore ``:current`` again.
   Otherwise those database copies will be dropped.
3. If you restore ``:previous`` with ``--reversible``,
   ``:current`` will now refer to the original ``:previous``
   and vice versa.

By default, reversible restores are turned off. They can be globally
enabled with ``settings.PGCLONE_REVERSIBLE`` or overridden on
a per-configuration basis with the ``reversible`` key.

.. tip::

    Restoring to ``:current`` or ``:previous`` with
    the ``--reversible`` flag is much faster than
    restoring from a dump key. Restoring without ``--reversible`` is even
    faster since databases are only renamed, but you lose
    the ability to revert again.