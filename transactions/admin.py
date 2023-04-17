from django.contrib import admin
from transactions.models import Amount, MoneyTransfer
# Register your models here.

admin.site.register(Amount)
admin.site.register(MoneyTransfer)