import ddf
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
import freezegun
import pytest


@pytest.fixture(autouse=True)
def patch_gethostname(mocker):
    mocker.patch("socket.gethostname", return_value="dev", autospec=True)


@freezegun.freeze_time("2020-07-01")
@pytest.mark.django_db(transaction=True)
def test_simple_dump_ls_restore(tmpdir, capsys, settings):
    """
    Tests a simple dump, ls, and restore, asserting that a user
    created after a dump is deleted upon restore
    """
    settings.PGCLONE_STORAGE_LOCATION = tmpdir.strpath

    call_command("pgclone", "ls")
    assert capsys.readouterr().out == ""

    with pytest.raises(SystemExit):
        call_command("pgclone", "restore", "dev/default/none/")
    assert capsys.readouterr().err.startswith("Could not find a dump key matching prefix")

    ddf.G("auth.User")
    call_command("pgclone", "dump")

    call_command("pgclone", "ls")
    assert capsys.readouterr().out == ("dev/default/none/2020-07-01-00-00-00-000000.dump\n")

    ddf.G("auth.User")
    assert User.objects.count() == 2

    call_command("pgclone", "restore", "dev/default/none")

    connection.connect()
    assert User.objects.count() == 1

    call_command(
        "pgclone",
        "restore",
        "dev/default/none/2020-07-01-00-00-00-000000.dump",
    )

    connection.connect()
    assert User.objects.count() == 1

    # Do some basic error assertions
    capsys.readouterr()
    with pytest.raises(SystemExit):
        call_command("pgclone", "dump", "--config", "bad_config_name")
    assert capsys.readouterr().err.startswith('"bad_config_name" is not a valid')

    with pytest.raises(SystemExit):
        call_command("pgclone", "restore")
    assert capsys.readouterr().err.startswith("Must provide a dump key")

    # Try restoring with custom swap hooks
    call_command("pgclone", "restore", "dev", "--pre-swap-hook", "migrate")
    connection.connect()
    assert User.objects.count() == 1

    # Dump and restore while ignoring the user table
    with freezegun.freeze_time("2020-07-02"):
        call_command("pgclone", "dump", "--exclude", "auth.User")
        assert User.objects.count() == 1

        call_command("pgclone", "restore", "dev/default/none/")
        connection.connect()
        assert not User.objects.exists()


@freezegun.freeze_time("2020-07-01")
@pytest.mark.django_db(transaction=True)
def test_reversible_dump_ls_restore(tmpdir, capsys, settings, mocker):
    """
    Tests a reversible dump, ls, and restore for local clones
    """
    settings.PGCLONE_STORAGE_LOCATION = tmpdir.strpath
    db_name = settings.DATABASES["default"]["NAME"]

    call_command("pgclone", "ls")
    assert capsys.readouterr().out == ""

    ddf.G("auth.User")
    call_command("pgclone", "dump")

    call_command("pgclone", "ls")
    assert capsys.readouterr().out == ("dev/default/none/2020-07-01-00-00-00-000000.dump\n")

    with pytest.raises(SystemExit):
        call_command("pgclone", "ls", "--instances", "--databases")
    assert capsys.readouterr().err.startswith("Can only use one of")

    call_command("pgclone", "ls", "--instances")
    assert capsys.readouterr().out == "dev\n"

    call_command("pgclone", "ls", "--configs")
    assert capsys.readouterr().out == "none\n"

    call_command("pgclone", "ls", "--databases")
    assert capsys.readouterr().out == "default\n"

    ddf.G("auth.User")
    assert User.objects.count() == 2

    call_command("pgclone", "restore", "dev", "--reversible")

    connection.connect()
    assert User.objects.count() == 1

    call_command("pgclone", "ls", "--local")
    output = capsys.readouterr().out
    assert f":{db_name}__curr" in output
    assert f":{db_name}__prev" in output

    ddf.G("auth.User")
    ddf.G("auth.User")
    assert User.objects.count() == 3

    # Use the special "previous" and "current" aliases
    # Restoring to the "current" will go back to the point at which
    # it was restored, which had exactly one user
    call_command("pgclone", "restore", ":current", "--reversible")
    connection.connect()
    assert User.objects.count() == 1

    # Going back to the "previous" takes us to the database before
    # the restore happened, which had three users
    call_command("pgclone", "restore", ":previous", "--reversible")
    connection.connect()
    assert User.objects.count() == 3

    # Going back to the "previous" again starts cycling through both
    # copies of the database
    call_command("pgclone", "restore", ":previous", "--reversible")
    connection.connect()
    assert User.objects.count() == 1

    # Dont use the special alias and instead directly reference the
    # local copy
    call_command("pgclone", "restore", f":{db_name}__prev")
    connection.connect()
    assert User.objects.count() == 3

    # Since we didn't restore with "reversible", there are no longer
    # current and previous copies
    assert capsys.readouterr()
    with pytest.raises(SystemExit):
        call_command("pgclone", "restore", ":previous")
    assert capsys.readouterr().err.startswith("Local database")

    with pytest.raises(SystemExit):
        call_command("pgclone", "restore", ":current")
    assert capsys.readouterr().err.startswith("Local database")
