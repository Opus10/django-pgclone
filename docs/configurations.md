# Configurations

Command options can be saved in `settings.PGCLONE_CONFIGS` for re-use. Here's an example:

```python
PGCLONE_CONFIGS = {
    # Ensure that prod dumps use a different storage location and
    # are always reversible
    "prod": {
        "storage_location": "s3://my-prod-bucket",
        "reversible": True,
        "instance": "prod"
    },
    # Make it so that dev dumps are always listed, dumped, and restored under
    # the same dump key prefix.
    "dev": {
        "dump_key": "dev/default/dev/",
        "reversible": True,
        "instance": "dev"
    },
    # Anonymous dumps always run the same pre-swap hooks
    "anonymized": {
        "pre_swap_hooks": ["anonymize_data"]
    },
    # This dump always ignores the users/groups models
    "no_users": {
        "exclude": ["auth.User", "auth.Group"] 
    },
    # Always supply the database argument when using a different DB
    "other_db": {
        "database": "my_other_database"
    }
}
```

Once defined, a config can supply default parameters to any command like so:

    python manage.py pgclone restore -c prod

The above command is equivalent to running:

    python manage.py pgclone restore --storage-location s3://my-prod-bucket --reversible

Keep in mind that the `instance` key from the `prod` config was not used since it's not an option for `restore`.

!!! note

    Check out the [basics](basics.md) sections for more information on how configurations help determine default values for command options.

## Configuration keys

The following keys can be supplied to configuration dictionaries:

* **database**: The `--database` option for all commands. Overrides `settings.PGCLONE_DATABASE`.
* **dump_key**: The positional argument for `restore` and `ls`.
* **exclude**: The `--exclude` options for `dump`. Overrides `settings.PGCLONE_EXCLUDE`.
* **instance**: The `--instance` option for `dump`. Overrides `settings.PGCLONE_INSTANCE`. 
* **pre_dump_hooks**: The `--pre-dump-hook` options for `dump`. Overrides `settings.PGCLONE_PRE_DUMP_HOOKS`.
* **pre_swap_hooks**: The `--pre-swap-hook` options for `restore`. Overrides `settings.PGCLONE_PRE_SWAP_HOOKS`.
* **reversible**: The `--reversible` option for `restore`. Overrides `settings.PGCLONE_REVERSIBLE`.
* **storage_location**: The `--storage-location` option for all commands. Overrides `settings.PGCLONE_STORAGE_LOCATION`.  
