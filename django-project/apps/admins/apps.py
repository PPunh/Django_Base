from django.apps import AppConfig


# make sure to update AppClassName and App name
class AdminsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'apps.admins'
    verbose_name = 'Admins'
    label = 'admins'
