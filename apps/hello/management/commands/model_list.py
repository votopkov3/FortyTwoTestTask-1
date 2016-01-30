from django.core.management.base import NoArgsCommand
from django.db.models import get_models


class Command(NoArgsCommand):

    help = 'Print all project models and the count of objects in every model'

    def handle(self, *args, **kwargs):
        for model in get_models():
            self.stderr.write("Error: %s.%s %d\n" %
                              (model.__module__, model.__name__,
                               model._default_manager.count()))
