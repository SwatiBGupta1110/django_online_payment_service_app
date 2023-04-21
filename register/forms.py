from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from transactions.models import Amount
import requests

# from .models import Register
from register.money_converter import currency_converter
from django.forms import ModelForm
#currency_converter("gbp", 1000, "dollars")

CURRENCY_CHOICES= [
    ('gbp', 'GBP'),
    ('usd', 'USD'),
    ('euros', 'EUROS'),
    ('inr', 'INR'),
]

class RegisterUser(UserCreationForm):
    firstname = forms.CharField(label="First name", max_length=100,required=True)
    lastname = forms.CharField(label="Last name", max_length=100,required=True)
    email = forms.EmailField(label="Email", max_length=100,required=True)
    primarycurrency = forms.CharField(label='Choose your primary currency here',
                                      widget=forms.Select(choices=CURRENCY_CHOICES),
                                      required=True)
    class Meta:
        model = User
        fields = ["firstname", "lastname", "email", "username", "primarycurrency",
                  "password1", "password2"]

    def save(self, *args, **kwargs):
        instance = super(RegisterUser, self).save(*args, **kwargs)
        currency_1 = currency_2 = "gbp"
        currency_2 = self.cleaned_data['primarycurrency']
        amount_of_currency1 = 1000
        if currency_1 != currency_2:
            money_conversion_api = f"http://127.0.0.1:8000/conversion/{currency_1}/{currency_2}/{amount_of_currency1}/"
            response = requests.get(money_conversion_api)
            if response.status_code == 200:
                print(response.json())
                data = response.json()

                converted_amount = data['converted_amount']
                Amount.objects.create(name=instance,primarycurrency=self.cleaned_data['primarycurrency'], amount=converted_amount,email=self.cleaned_data['email'])
            else:
                print('Error:', response.status_code)
        else:
            converted_amount = amount_of_currency1
            Amount.objects.create(name=instance, primarycurrency=self.cleaned_data['primarycurrency'], amount=converted_amount, email=self.cleaned_data['email'])
        return instance
