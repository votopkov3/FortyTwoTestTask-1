from apps.hello.models import LogEntrry
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

exclude_models_name = ['LogEntrry', 'ContentType',
                       'LogEntry', 'MigrationHistory']


@receiver(post_save)
def post_save_signal(sender, created, **kwargs):
    if created and sender.__name__ in exclude_models_name:
        return
    status = 'Create' if created else 'Update'
    LogEntrry.objects.create(title=sender.__name__, status=status)


@receiver(post_delete)
def post_delete_signal(sender, **kwargs):
    LogEntrry.objects.create(title=sender.__name__, status='Delete')
    return
