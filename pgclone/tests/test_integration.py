import ddf
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
import freezegun
import pytest

import pgclone.exceptions


@freezegun.freeze_time('2020-07-01')
@pytest.mark.django_db(transaction=True)
def test_simple_dump_ls_restore(tmpdir, capsys, settings):
    """
    Tests a simple dump, ls, and restore, asserting that a user
    created after a dump is deleted upon restore
    """
    db_name = settings.DATABASES['default']['NAME']
    settings.PGCLONE_STORAGE_LOCATION = tmpdir.strpath

    call_command('pgclone', 'ls')
    assert capsys.readouterr().out == ''

    with pytest.raises(RuntimeError):
        call_command('pgclone', 'restore', db_name)

    ddf.G('auth.User')
    call_command('pgclone', 'dump')

    call_command('pgclone', 'ls')
    assert capsys.readouterr().out == (
        f'{db_name}/2020_07_01_00_00_00_000000.default.dump\n'
    )

    ddf.G('auth.User')
    assert User.objects.count() == 2

    call_command('pgclone', 'restore', db_name)

    connection.connect()
    assert User.objects.count() == 1

    call_command(
        'pgclone',
        'restore',
        f'{db_name}/2020_07_01_00_00_00_000000.default.dump',
    )

    connection.connect()
    assert User.objects.count() == 1

    # Do some basic error assertions
    with pytest.raises(pgclone.exceptions.ConfigurationError):
        call_command('pgclone', 'dump', '-c bad_config_name')

    with pytest.raises(pgclone.exceptions.ConfigurationError):
        call_command('pgclone', 'restore', db_name, '-c bad_config_name')

    # Try restoring with custom swap hooks
    call_command('pgclone', 'restore', db_name, '--pre-swap-hook', 'migrate')
    connection.connect()
    assert User.objects.count() == 1

    # Dump and restore while ignoring the user table
    with freezegun.freeze_time('2020-07-02'):
        call_command('pgclone', 'dump', '--exclude-model', 'auth.User')
        assert User.objects.count() == 1

        call_command('pgclone', 'restore', db_name)
        connection.connect()
        assert not User.objects.exists()


@freezegun.freeze_time('2020-07-01')
@pytest.mark.django_db(transaction=True)
def test_reversible_dump_ls_restore(tmpdir, capsys, settings):
    """
    Tests a reversible dump, ls, and restore for local clones
    """
    db_name = settings.DATABASES['default']['NAME']
    settings.PGCLONE_STORAGE_LOCATION = tmpdir.strpath

    call_command('pgclone', 'ls')
    assert capsys.readouterr().out == ''

    ddf.G('auth.User')
    call_command('pgclone', 'dump')

    call_command('pgclone', 'ls')
    assert capsys.readouterr().out == (
        f'{db_name}/2020_07_01_00_00_00_000000.default.dump\n'
    )

    call_command('pgclone', 'ls', '--only-db-names')
    assert capsys.readouterr().out == f'{db_name}\n'

    ddf.G('auth.User')
    assert User.objects.count() == 2

    call_command('pgclone', 'restore', db_name, '--reversible')

    connection.connect()
    assert User.objects.count() == 1

    call_command('pgclone', 'ls', '--local')
    output = capsys.readouterr().out
    assert f':{db_name}__curr' in output
    assert f':{db_name}__prev' in output

    ddf.G('auth.User')
    ddf.G('auth.User')
    assert User.objects.count() == 3

    # Use the special "previous" and "current" aliases
    # Restoring to the "current" will go back to the point at which
    # it was restored, which had exactly one user
    call_command('pgclone', 'restore', ':current', '--reversible')
    connection.connect()
    assert User.objects.count() == 1

    # Going back to the "previous" takes us to the database before
    # the restore happened, which had three users
    call_command('pgclone', 'restore', ':previous', '--reversible')
    connection.connect()
    assert User.objects.count() == 3

    # Going back to the "previous" again starts cycling through both
    # copies of the database
    call_command('pgclone', 'restore', ':previous', '--reversible')
    connection.connect()
    assert User.objects.count() == 1

    # Dont use the special alias and instead directly reference the
    # local copy
    call_command('pgclone', 'restore', f':{db_name}__prev')
    connection.connect()
    assert User.objects.count() == 3

    # Since we didn't resotre with "reversible", there are no longer
    # current and previous copies
    with pytest.raises(RuntimeError, match='does not exist'):
        call_command('pgclone', 'restore', ':previous')

    with pytest.raises(RuntimeError, match='does not exist'):
        call_command('pgclone', 'restore', ':current')
