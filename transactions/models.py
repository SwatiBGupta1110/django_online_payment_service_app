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
    email = models.EmailField(max_length=100)

    def __str__(self):
        return f"{self.name},{self.primarycurrency}, {self.amount}"


class MoneyTransfer(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('owed', 'Owed'),
        ('paid', 'Paid'),
        ('received', 'Received'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
        ('declined', 'Declined'),
    )
    request_id = models.PositiveSmallIntegerField(default=0000)
    payer_email_address = models.EmailField(max_length=100) #payer --> the  one making a payment
    payee_email_address = models.EmailField(max_length=100) #payee -->the one receiving the payment
    amount_to_transfer_to_payee = models.DecimalField(max_digits=10, decimal_places=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payer_currency = models.CharField(max_length=100, default="gbp")
    payee_currency = models.CharField(max_length=100, default="gbp")
    date = models.DateField(default=datetime.now)

    def __str__(self):
        return f"{self.payer_email_address}, {self.payee_email_address}, {self.amount_to_transfer_to_payee},{self.status} "
