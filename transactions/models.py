from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
# from money_converter import currency_converter
import requests
# Create your models here.

class Amount(models.Model):

    name = models.ForeignKey(User, on_delete=models.CASCADE)
    primarycurrency = models.CharField(max_length=100, default="gbp")
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    email = models.EmailField(max_length=100,default="your_email")

    # def amount(self):
    #     calculated_amount = currency_converter(self.primarycurrency, 1000)
    #     return calculated_amount
    #
    #     if self.primarycurrency == "gbp":
    #         calculated_amount = 1000
    #         return calculated_amount
    #     else:
    #         #currency_converter("gbp","dollars",1000)
    #         base_currency = "gbp"
    #         calculated_amount = currency_converter(base_currency, self.primarycurrency, 1000)
    #         return calculated_amount

    def __str__(self):
        return f"{self.name},{self.primarycurrency}, {self.amount}"


class MoneyTransfer(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
    )
    # enter_your_email_address = models.ForeignKey(User, on_delete=models.CASCADE,related_name='your_money_transfers',to_field="email")
    # enter_payee_email_address = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payee_money_transfers',to_field="email")
    payer_email_address = models.EmailField(max_length=100,default="your_email") #payer --> the  one making a payment
    payee_email_address = models.EmailField(max_length=100,default="your_email") #payee -->the one receiving the payment
    amount_to_transfer_to_payee = models.DecimalField(max_digits=10, decimal_places=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payer_currency = models.CharField(max_length=100, default="gbp")
    payee_currency = models.CharField(max_length=100, default="gbp")
    date = models.DateField(default=datetime.now)

    def __str__(self):
        return f"{self.payer_email_address}, {self.payee_email_address}, {self.amount_to_transfer_to_payee},{self.status} "
