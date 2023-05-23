.. _faq:

Frequently Asked Questions
==========================

How can I avoid destroying a database?
--------------------------------------

If you'd like to avoid accidentally restoring a production database, for example,
set ``settings.PGCLONE_ALLOW_RESTORE`` to ``False``.

:ref:`hooks` can also be used to fail the dump or restore process. For example, one could fail a
dump in a hook if the hook notices that it's data that isn't anonymized.

If storage or lengthier restore times are not a concern, you can also
configure :ref:`Reversible Restores <reversible>` to happen by default, allowing you to
restore back to the previous version if it was a mistake.

What other ways can I protect accidental incorrect usage?
---------------------------------------------------------

All core commands (``dump``, ``restore``, and ``copy``) have associated ``PGCLONE_ALLOW_*``
options. In a production environment, setting
``settings.PGCLONE_ALLOW_RESTORE`` and ``settings.PGCLONE_ALLOW_COPY`` to ``False`` are good ideas. If you
have sensitive data that should not be dumped to outside storage, set
``settings.PGCLONE_ALLOW_DUMP`` to ``False``.

``pg_restore`` shows errors but succeeded. What happened?
---------------------------------------------------------

When running ``python manage.py pgclone restore``, you may see some error output from
``pg_restore``. Some errors are legitimate and affect the database from being restored, while
others may be benign. For example, RDS restores often report errors that are meaningless and
simply cannot be suppressed.

Migrations run by default during restores unless the pre-swap hooks are overridden. Successful
migrations are usually a good way to ensure a ``pg_restore`` was actually successful. We're still
working on better ways to address this issue.

How do I migrate to version 2.0?
--------------------------------

Version 2 changes the configuration hierarchy and dump key formats. Keep the following in mind when migrating from version 1:

1. ``settings.PGCLONE_DUMP_CONFIGS`` and ``settings.PGCLONE_RESTORE_CONFIGS`` were merged into ``settings.PGCLONE_CONFIGS``.
   Configs closely map to the options allowed by all the commands. See :ref:`configurations`.
2. Dump keys are now in the format of ``<instance>/<database>/<config>/<timestamp>.dump``. If you'd like to use
   old dumps, set ``settings.PGCLONE_VALIDATE_DUMP_KEYS`` to ``False``. Old dump keys aren't compatible with the
   ``--instances``, ``--configs``, or ``--databases`` options for ``ls``.
3. Users no longer need to install and configure ``django-pgconnection`` for ``settings.DATABASES``. You can remove
   this dependency and no longer wrap the database settings.

How can I contact the author?
-----------------------------

The primary author, Wes Kendall, loves to talk to users. Message him at `wesleykendall@protonmail.com <mailto:wesleykendall@protonmail.com>`__ for any feedback. Any questions, feature requests, or bugs should
be reported as `issues here <https://github.com/Opus10/django-pgclone/issues>`__.

Wes and other `Opus 10 engineers <https://opus10.dev>`__ do contracting work, so keep them in mind if your company
uses Django.
