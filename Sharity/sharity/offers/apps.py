from django.apps import AppConfig



class OffersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'offers'

    def ready(self):
        from actstream import registry
        from django.contrib.auth.models import User
        registry.register(User)
        registry.register(self.get_model('Offer'))

