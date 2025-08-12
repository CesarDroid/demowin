from django.apps import AppConfig

class MufasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mufas'  # ← Nombre simple, sin label personalizado
    verbose_name = 'Mufas'
    
    def ready(self):
        import mufas.signals