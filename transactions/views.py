import json
from datetime import date

from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, OperationalError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from . import models
from transactions.forms import MoneyTransferForm
from django.contrib import messages
import requests

from .models import MoneyTransfer, Amount


# Create your views here.


@transaction.atomic
def amount_transfer(request):
    global is_tr_cmt
    is_tr_cmt = False
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST)
        if form.is_valid():
            src_email = form.cleaned_data["payer_email_address"]
            payee_email = form.cleaned_data["payee_email_address"]
            amount_to_transfer = form.cleaned_data["amount_to_transfer_to_payee"]

            src_amount = models.Amount.objects.select_related().get(name__email=src_email)
            payee_amount = models.Amount.objects.select_related().get(name__email=payee_email)

            src_currency = src_amount.primarycurrency
            payee_currency = payee_amount.primarycurrency

            converted_amount = amount_to_transfer #Initially
            try:
                with transaction.atomic():
                    if src_currency != payee_currency:
                        api_url = f"http://127.0.0.1:8000/conversion/{src_currency}/{payee_currency}/{amount_to_transfer}/"
                        response = requests.get(api_url)
                        if response.status_code == 200:
                            print(response.json())
                            data = response.json()
                            converted_amount = data['converted_amount']
                        else:
                            print('Error:', response.status_code)
                    else:
                        converted_amount = amount_to_transfer
                    src_amount.amount = src_amount.amount - amount_to_transfer
                    src_amount.save()

                    payee_amount.amount = payee_amount.amount + converted_amount
                    payee_amount.save()
                    is_tr_cmt = True
                    transfer = MoneyTransfer.objects.create(payer_email_address=src_email,
                                                            payee_email_address=payee_email,
                                                            amount_to_transfer_to_payee=converted_amount,
                                                            status="sent",
                                                            payer_currency=src_currency,
                                                            payee_currency=payee_currency,
                                                            date=date.today())
            except OperationalError:
                messages.info(request, f"Transfer operation is not possible now.")
            if is_tr_cmt==True:
                @transaction.on_commit
                def call_on_commit():
                    print("Transaction committed")
                    messages.success(request, "Amount transfer successful.")
        # transaction.on_commit()
        return render(request, "transactions/old_amount.html", {"src_email":src_email, "src_currency":src_currency,
                                                            "src_amount": src_amount,"payee_email":payee_email,
                                                            "payee_currency":payee_currency,
                                                            "payee_amount": payee_amount,
                                                            "tr_comt":"Transaction Committed"})
    else:
        form = MoneyTransferForm()
    return render(request, "transactions/amounttransfer.html", {"form": form})


@transaction.atomic
def request_money(request): # click on send
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST)
        if form.is_valid():
            src_email = form.cleaned_data["enter_your_email_address"]
            payee_email = form.cleaned_data["enter_payee_email_address"]
            amount_to_transfer = form.cleaned_data["enter_amount_to_transfer"]

            src_amount = models.Amount.objects.select_related().get(name__email=src_email)
            payee_amount = models.Amount.objects.select_related().get(name__email=payee_email)

            src_currency = src_amount.primarycurrency
            payee_currency = payee_amount.primarycurrency

            converted_amount = amount_to_transfer #Initially
            try:
                with transaction.atomic():
                    if src_currency != payee_currency:
                        api_url = f"http://127.0.0.1:8000/conversion/{src_currency}/{payee_currency}/{amount_to_transfer}/"
                        response = requests.get(api_url)
                        if response.status_code == 200:
                            print(response.json())
                            data = response.json()
                            converted_amount = data['converted_amount']
                        else:
                            print('Error:', response.status_code)
                    else:
                        converted_amount = amount_to_transfer
                    src_amount.amount = src_amount.amount - amount_to_transfer
                    src_amount.save()

                    payee_amount.amount = payee_amount.amount + converted_amount
                    payee_amount.save()
                    is_tr_cmt = True
                    transfer = MoneyTransfer.objects.create(payer_email_address=src_email,
                                                            payee_email_address=payee_email,
                                                            amount_to_transfer_to_payee=converted_amount,
                                                            status="sent",
                                                            payer_currency=src_currency,
                                                            payee_currency=payee_currency,
                                                            date=date.today())
            except OperationalError:
                messages.info(request, f"Transfer operation is not possible now.")
            if is_tr_cmt==True:
                @transaction.on_commit
                def call_on_commit():
                    print("Transaction committed")
                    messages.success(request, "Amount transfer successful.")
        # transaction.on_commit()
        return render(request, "transactions/old_amount.html", {"src_email":src_email, "src_currency":src_currency,
                                                            "src_amount": src_amount,"payee_email":payee_email,
                                                            "payee_currency":payee_currency,
                                                            "payee_amount": payee_amount,
                                                            "tr_comt":"Transaction Committed"})
    else:
        form = MoneyTransferForm()
    return render(request, "transactions/amounttransfer.html", {"form": form})

def get_all_payers(request):
    # queryset = User.objects.filter(~Q(email=request.user.email)).values_list("email")
    queryset = Amount.objects.filter(~Q(email=request.user.email)).values_list("email")
    serialize_querset = json.dumps(list(queryset), cls=DjangoJSONEncoder)
    return JsonResponse(serialize_querset, safe=False)