from django.apps import AppConfig


class EgameConfig(AppConfig):
    name = 'egame'

    def ready(self):
        from . import signals