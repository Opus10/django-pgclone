# Local Copies

Some database dump and restore flows can be facilitated by making local copies so that they can be quickly restored later (as opposed to a full restore with `pg_restore`). This can be accomplished with the `pgclone copy` command.

The `pgclone copy` command will copy the current database to a target database name using `CREATE DATABASE <source> TEMPLATE <target>`. The command takes a local dump key, which is just the database name prefixed with `:`.

In other words, you can do the following to copy your default database to another database called `my_backup`:

    python manage.py pgclone copy :my_backup

And then you can restore it with the following:

    python manage.py pgclone restore :my_backup

!!! note

    You cannot use `:pre` or `:post` as the target database name. These are reserved for reversible restores.

!!! danger

    Calling `pgclone copy` will take out an exclusive access lock on the default database when copying it, preventing all activity until the copy is done. Use with caution, and never run this in a production environment.