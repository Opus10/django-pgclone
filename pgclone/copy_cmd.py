from pgclone import db, exceptions, logging, options, settings


def _copy(*, dump_key, database):
    """
    Copy implementation
    """
    if not settings.allow_copy():  # pragma: no cover
        raise exceptions.RuntimeError("Copy not allowed.")

    source_db = db.conf(using=database)

    if not dump_key or dump_key == ":current":
        dump_key = ":current"
        target_db_name = f'{source_db["NAME"]}__curr'
    elif dump_key == ":previous":
        target_db_name = f'{source_db["NAME"]}__prev'
    else:
        if not dump_key.startswith(":"):  # pragma: no cover
            raise RuntimeError('Copy target must start with ":"')

        target_db_name = dump_key[1:]

    target_db = db.make(target_db_name, using=database, check=False)

    if source_db == target_db:  # pragma: no cover
        raise exceptions.RuntimeError("Target database cannot be the same as source database.")

    logging.success_msg("Creating copy")
    db.drop(target_db, using=database)
    copy_db_sql = f"""
        CREATE DATABASE "{target_db['NAME']}"
            WITH TEMPLATE
        "{source_db['NAME']}"
    """
    db.kill_connections(source_db, using=database)
    db.psql(copy_db_sql, using=database)

    logging.success_msg(f'Successfully copied database "{database}" to "{dump_key}"')

    return dump_key


def copy(dump_key=None, *, database=None, config=None):
    """
    Copies a database using ``CREATE DATABASE <dump_key> TEMPLATE <database>``.

    Note that we use dump keys with the same syntax that ``dump`` and ``restore``
    commands take. Since ``copy`` only works with local database copies, this
    means the dump keys are always the database name prefixed with ``:``.

    Args:
        dump_key (str, default=None): A name to use for the copy. Must be prefixed
            with ``:`` and only consist of valid database name characters.
            If ``None``, ``:{database}__curr`` is used as the key.
        database (str, default=None): The database to copy.
        config (str, default=None): The configuration name
            from ``settings.PGCLONE_CONFIGS``.

    Returns:
        str: The dump key that was copied.
    """
    opts = options.get(
        dump_key=dump_key,
        config=config,
        database=database,
    )

    return _copy(dump_key=opts.dump_key, database=opts.database)
