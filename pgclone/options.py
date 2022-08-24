from pgclone import exceptions, settings


def _first_non_none(*values):
    for value in values:  # pragma: no branch
        if value is not None:
            return value


class _Options:
    def __init__(
        self,
        *,
        config=None,
        dump_key=None,
        reversible=None,
        exclude=None,
        pre_swap_hooks=None,
        pre_dump_hooks=None,
        instance=None,
        database=None,
        storage_location=None,
    ):
        """Parse options for pgclone commands

        Options follow the hierarchy of:

        1. Settings are the default
        2. Any configurations override settings
        3. Any direct parameters override configurations
        """
        if config and config not in settings.configs():
            raise exceptions.ValueError(
                f'"{config}" is not a valid configuration in settings.PGCLONE_CONFIGS.'
            )

        config_opts = settings.configs()[config] if config else {}

        # exlude and hooks alter the result, so we label this a "none"
        # config even if it starts from a pre-defined config
        if (
            not config
            or exclude is not None
            or pre_dump_hooks is not None
            or pre_swap_hooks is not None
        ):
            config = "none"

        # Generate options based on hierarchy
        self.dump_key = dump_key or config_opts.get("dump_key")
        self.instance = instance or config_opts.get("instance") or settings.instance()
        self.database = database or config_opts.get("database") or settings.database()
        self.storage_location = (
            storage_location or config_opts.get("storage_location") or settings.storage_location()
        )
        self.reversible = (
            _first_non_none(reversible, config_opts.get("reversible"), settings.reversible())
            or False
        )
        self.pre_dump_hooks = (
            _first_non_none(
                pre_dump_hooks, config_opts.get("pre_dump_hooks"), settings.pre_dump_hooks()
            )
            or []
        )
        self.pre_swap_hooks = (
            _first_non_none(
                pre_swap_hooks, config_opts.get("pre_swap_hooks"), settings.pre_swap_hooks()
            )
            or []
        )
        self.exclude = (
            _first_non_none(exclude, config_opts.get("exclude"), settings.exclude()) or []
        )
        self.config = config


def get(**kwargs):
    return _Options(**kwargs)
