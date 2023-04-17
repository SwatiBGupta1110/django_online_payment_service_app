from django import forms
from . import models


class MoneyTransferForm(forms.ModelForm):
    class Meta:
        model = models.MoneyTransfer
        fields = ["payer_email_address", "payee_email_address", "amount_to_transfer_to_payee"]