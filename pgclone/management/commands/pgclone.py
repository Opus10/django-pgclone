from django.core.management.base import BaseCommand

from pgclone import dump
from pgclone import logging
from pgclone import ls
from pgclone import restore


class SubCommands(BaseCommand):
    """
    Subcommand class vendored in from
    https://github.com/andrewp-as-is/django-subcommands.py
    because of installation issues
    """

    argv = []
    subcommands = {}

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            dest='subcommand', title='subcommands', description=''
        )
        subparsers.required = True

        for command_name, command_class in self.subcommands.items():
            command = command_class()

            subparser = subparsers.add_parser(
                command_name, help=command_class.help
            )
            command.add_arguments(subparser)

            command_parser = command.create_parser('manage.py', 'pgclone')
            subparser._actions = command_parser._actions

    def run_from_argv(self, argv):  # pragma: no cover
        self.argv = argv
        return super().run_from_argv(argv)

    def handle(self, *args, **options):
        command_name = options['subcommand']
        self.subcommands.get(command_name)
        if command_name not in self.subcommands:  # pragma: no cover
            raise ValueError('unknown subcommand: %' % command_name)
        command_class = self.subcommands[command_name]

        if len(self.argv):  # pragma: no cover
            args = [self.argv[0]] + self.argv[2:]
            return command_class().run_from_argv(args)
        return command_class().execute(*args, **options)


class DumpCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--exclude-model',
            nargs='*',
            dest='exclude_models',
            help='Model(s) you wish to exclude when dumping',
        )
        parser.add_argument(
            '-c',
            '--dump-config',
            dest='dump_config_name',
            help=(
                'The dump configuration name from'
                ' settings.PGCLONE_DUMP_CONFIGS'
            ),
        )

    def handle(self, *args, **options):
        logger = logging.new_stdout_logger()
        with logging.set_logger(logger):
            dump(
                exclude_models=options['exclude_models'],
                dump_config_name=options['dump_config_name'],
            )


class LsCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'db_name', nargs='?', help='The database name to list'
        )
        parser.add_argument(
            '--only-db-names',
            action='store_true',
            help='Only list database names',
        )
        parser.add_argument(
            '--local', action='store_true', help='Only list local restore keys'
        )

    def handle(self, *args, **options):
        results = ls(
            db_name=options['db_name'],
            only_db_names=options['only_db_names'],
            local=options['local'],
        )
        for dump_name in results:
            print(dump_name)


class RestoreCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'db_name_or_dump_key',
            help='The database name or dump key to restore',
        )
        parser.add_argument(
            '--pre-swap-hook',
            nargs='*',
            dest='pre_swap_hooks',
            help=(
                'Management command(s) that should be executed on'
                ' the restored database before it is swapped to the'
                ' primary database.'
            ),
        )
        parser.add_argument(
            '-c',
            '--restore-config',
            dest='restore_config_name',
            help=(
                'The restore configuration name from'
                ' settings.PGCLONE_RESTORE_CONFIGS'
            ),
        )
        parser.add_argument(
            '--reversible',
            dest='reversible',
            action='store_true',
            help=(
                'Create 2 extra local databases for quicker future '
                'restoration at the cost of a longer initial restore.'
            ),
        )

    def handle(self, *args, **options):
        logger = logging.new_stdout_logger()
        with logging.set_logger(logger):
            restore(
                options['db_name_or_dump_key'],
                pre_swap_hooks=options['pre_swap_hooks'],
                restore_config_name=options['restore_config_name'],
                reversible=options['reversible'],
            )


class Command(SubCommands):
    subcommands = {
        'dump': DumpCommand,
        'ls': LsCommand,
        'restore': RestoreCommand,
    }
