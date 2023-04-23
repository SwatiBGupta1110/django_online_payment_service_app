from django.apps import AppConfig

# configures Register app in the Django project
class RegisterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "register"