from django.apps import AppConfig


class MydocApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mydoc_api'

    def ready(self):
        import mydoc_api.signals


        
