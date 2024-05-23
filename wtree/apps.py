from django.apps import AppConfig


class WtreeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wtree'

    def ready(self):
        import wtree.signals
