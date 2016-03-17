from sys import stderr, stdout
from django.core.management.base import BaseCommand
from django.db import OperationalError
from django.db.models import get_models
from optparse import make_option


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--stdout',
                    action='store_true',
                    dest='stdout',
                    default=False,
                    help='output to STDOUT'),
        make_option('--stderr',
                    action='store_true',
                    dest='stderr',
                    default=False,
                    help='Output to STDERR'),
    )

    def handle(self, *args, **options):

        if options['stdout']:
            try:
                for model in get_models():
                    stdout.write("%s.%s %d\n" %
                                 (model.__module__, model.__name__,
                                  model.objects.count()))
            except OperationalError:
                stderr.write("Error: Make syncdb and migrate")

        if options['stderr']:
            try:
                for model in get_models():
                    stderr.write("Error: %s.%s %d\n" %
                                 (model.__module__, model.__name__,
                                  model.objects.count()))
            except OperationalError:
                stderr.write("Error: Make syncdb and migrate")
