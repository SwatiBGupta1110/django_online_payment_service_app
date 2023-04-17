from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Rate(models.Model):
    currency1 = models.CharField(max_length=200, default="gbp")
    currency2 = models.CharField(max_length=200, default="gbp")
    rate = models.DecimalField(max_digits=10, decimal_places=4, default=1)

    def __str__(self):
        return f"{self.currency1 },{self.currency2}, {self.rate}"

# class Conversion_Data(models.Model):
#     currency_1 = models.CharField(max_length=200, default="gbp")
#     amount = models.DecimalField(max_digits=10, decimal_places=2, default=1)
#     currency_2 = models.CharField(max_length=200,default="gbp")
#     converted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1)
#     name = models.ForeignKey(User, on_delete=models.DO_NOTHING)
#     date = models.DateField()
#
#     def __str__(self):
#         return f"{self.amount}, {self.currency_1 },{self.converted_amount}, {self.currency_2}"