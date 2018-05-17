from django.apps import AppConfig


class EplnConfig(AppConfig):
    name = 'epln'

    def ready(self):
        from . import signals
