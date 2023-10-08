# Hooks

Hooks are management commands that execute during the dump and restore process, specifically:

* **Pre-swap hooks**: Executed before the restored temporary database is swapped into the main database.
* **Pre-dump hooks**: Executed before a database is dumped.

## Pre-swap

Pre-swap management commands run on the temporary database right before it is swapped. Here's an example of running both `migrate` and `remove_stale_contenttypes` before swapping in the restored database:

    python manage.py pgclone restore --pre-swap-hook migrate --pre-swap-hook remove_stale_contenttypes

By doing this, we ensure that a dump has been successfully migrated before it is swapped in. This also provides us with the opportunity to run custom management commands, for example, anonymizing data for local development purposes.

Any management command errors will prevent the restore from finishing, leaving the temporary database without affecting the main one.

!!! note

    Pre-swap hooks can be globally configured with `settings.PRE_SWAP_HOOKS` or on a per-configuration basis with `pre_swap_hooks`. Settings default to running `migrate`.

## Pre-dump

Pre-dump hooks run on the main database before it is dumped.

!!! danger

    Unlike pre-swap hooks, pre-dump hooks run on a live database. Only use pre-dump hooks that will not affect the usability of your application.

Here's an example of running a custom management command called `prep_db_for_rds_dump`:

    python manage.py pgclone dump --pre-dump-hook prep_db_for_rds_dump

!!! note

    Pre-dump hooks can be globally configured with `settings.PRE_DUMP_HOOKS` or on a per-configuration basis with `pre_dump_hooks`.

## Designing Hooks

Hooks should only use the default database connection. `django-pgclone` takes care of routing database traffic in the management command during hook execution, ensuring that:

1. Pre-swap hooks are always executed against the correct temporary database.
2. Dumping and restoring in a multi-database environment runs hooks against the correct database.

!!! note

    Even if your application writes to a non-default database in hooks, the database traffic will still be routed to the proper database.
