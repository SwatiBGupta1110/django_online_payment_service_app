from django.apps import AppConfig

# configures Transactions app in the Django project
class TransactionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transactions"
