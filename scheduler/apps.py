from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import scheduler.signals
