from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Rate models saves all the conversion rates of different currencies avaialble in this app which are usd, euros, gbp, inr.
class Rate(models.Model):
    currency1 = models.CharField(max_length=200, default="gbp")
    currency2 = models.CharField(max_length=200, default="gbp")
    rate = models.DecimalField(max_digits=10, decimal_places=4, default=1)

    def __str__(self):
        return f"{self.currency1 },{self.currency2}, {self.rate}"
