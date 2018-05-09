from django.apps import AppConfig


class EtransportConfig(AppConfig):
    name = 'etransport'


    def ready(self):
        from . import signals