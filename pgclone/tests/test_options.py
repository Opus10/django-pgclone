import socket

from pgclone import options


def test_defaults():
    """Ensures settings are used as defaults"""
    opts = options.get()
    assert opts.dump_key is None
    assert opts.instance == socket.gethostname()
    assert opts.database == "default"
    assert opts.storage_location == ".pgclone/"
    assert opts.reversible is False
    assert opts.pre_dump_hooks == []
    assert opts.pre_swap_hooks == ["migrate"]
    assert opts.exclude == []
    assert opts.config == "none"


def test_config_overrides(settings):
    """Tests that configs override settings"""
    settings.PGCLONE_CONFIGS = {
        "config": {
            "dump_key": "dump_key",
            "instance": "instance",
            "database": "database",
            "storage_location": "storage_location",
            "reversible": "reversible",
            "pre_dump_hooks": ["pre_dump_hooks"],
            "pre_swap_hooks": ["pre_swap_hooks"],
            "exclude": ["exclude"],
        }
    }

    opts = options.get(config="config")
    assert opts.dump_key == "dump_key"
    assert opts.instance == "instance"
    assert opts.database == "database"
    assert opts.storage_location == "storage_location"
    assert opts.reversible == "reversible"
    assert opts.pre_dump_hooks == ["pre_dump_hooks"]
    assert opts.pre_swap_hooks == ["pre_swap_hooks"]
    assert opts.exclude == ["exclude"]
    assert opts.config == "config"


def test_direct_options(settings):
    """Verifies that supplied options override configs"""
    settings.PGCLONE_CONFIGS = {
        "config": {
            "dump_key": "dump_key",
            "instance": "instance",
            "database": "database",
            "storage_location": "storage_location",
            "reversible": "reversible",
            "pre_dump_hooks": ["pre_dump_hooks"],
            "pre_swap_hooks": ["pre_swap_hooks"],
            "exclude": ["exclude"],
        }
    }

    opts = options.get(
        config="config",
        dump_key="dump_key2",
        instance="instance2",
        database="database2",
        storage_location="storage_location2",
        reversible="reversible2",
        pre_dump_hooks=["pre_dump_hooks2"],
        pre_swap_hooks=["pre_swap_hooks2"],
        exclude=["exclude2"],
    )
    assert opts.dump_key == "dump_key2"
    assert opts.instance == "instance2"
    assert opts.database == "database2"
    assert opts.storage_location == "storage_location2"
    assert opts.reversible == "reversible2"
    assert opts.pre_dump_hooks == ["pre_dump_hooks2"]
    assert opts.pre_swap_hooks == ["pre_swap_hooks2"]
    assert opts.exclude == ["exclude2"]
    assert opts.config == "none"
