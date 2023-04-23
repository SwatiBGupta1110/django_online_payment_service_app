from django import forms
from . import models


"""
This form helps us in creating fields so that user can transfer the money and we need not use html
for creating form for user. It uses the MoneyTransfer model to save its data.
"""
class MoneyTransferForm(forms.ModelForm):
    class Meta:
        model = models.MoneyTransfer
        fields = ["payer_email_address", "payee_email_address", "amount_to_transfer_to_payee"]