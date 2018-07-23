from django.apps import AppConfig


class MpulsaConfig(AppConfig):
    name = 'mpulsa'

    def ready(self):
        from . import signals