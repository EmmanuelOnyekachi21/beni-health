from django.apps import AppConfig


class EnrolleesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.enrollees'

    def ready(self):
        import apps.enrollees.signals

