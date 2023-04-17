# from django.db import models
# from django.contrib.auth.models import User
# from djmoney.models.fields import MoneyField
#
#
# CURRENCY_CHOICES= [
#     ('gbp', 'GBP'),
#     ('dollars', 'DOLLARS'),
#     ('euros', 'EUROS'),
#     ('inr', 'INR'),
# ]
#
# # Create your models here.
# class Register(models.Model):
#     firstname = models.CharField( max_length=100)             # New variable,name is charField has label "Insert a name" len=100
#     lastname = models.CharField(max_length=100)
#     email=models.EmailField(max_length=100,primary_key=True,unique=True)
#     primarycurrency=models.CharField(default="gbp",max_length=100, choices=CURRENCY_CHOICES)
#     wallet_balance=models.IntegerField(default=1000)
#     address=models.CharField( max_length=100)
#     age=models.IntegerField(default=18)
#     username= models.CharField(max_length=100)
#     password1=models.CharField(max_length=50)
#     password2=models.CharField(max_length=50)
#     date = models.DateField()
#
#     def __str__(self):
#         return self.firstname +self.email
