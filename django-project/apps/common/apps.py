from django.apps import AppConfig


# make sure to update AppClassName and App name
class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'apps.common'
    verbose_name = 'Common'
    label = 'common'
