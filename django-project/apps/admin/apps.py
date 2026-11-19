from django.apps import AppConfig


# make sure to update AppClassName and App name
class AdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'apps.admin'
    verbose_name = 'Admin'
    label = 'admin'
