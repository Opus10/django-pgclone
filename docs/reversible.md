# Reversible Restores

The `--reversible` option of `manage.py pgclone restore` keeps the copy of the database before the restore (i.e. the "pre" restore point) and after the restore (i.e. the "post" restore point).

When using this option, you can then quickly revert to the point after the most recent restore with:

    python manage.py pgclone restore :post

Or to the point before the most recent restore with:

    python manage.py pgclone restore :pre

Keep the following in mind when using `--reversible`:

1. Restores take longer because an additional copy is made.
2. If you restore to the `:pre` or `:post` points, the `--reversible` option has no effect. It only has an effect when restoring database dumps.
3. The previous point also applies to restoring local copies made using `pgclone copy`. See [Local Copies](local_copies.md) for more information.

By default, reversible restores are turned off. They can be globally enabled with `settings.PGCLONE_REVERSIBLE` or overridden on a per-configuration basis with the `reversible` key.

!!! tip

    Restoring to `:pre` or `:post` with the `--reversible` flag is much faster than restoring from a dump key. Keep this in mind if you are frequently needing to restore back to these points in time, such as testing migrations or having a clean slate for acceptance testing.