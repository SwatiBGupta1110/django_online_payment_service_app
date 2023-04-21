import json
from datetime import date
import json
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, OperationalError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from . import models
from transactions.forms import MoneyTransferForm
from django.contrib import messages
import requests
from decimal import Decimal
import random
from .models import MoneyTransfer, Amount

# Create your views here.
currency_dict = {'gbp': 'GBP', 'usd': 'USD', 'euros': 'EUROS', 'inr': 'INR'}


@csrf_protect
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

            request_id = generate_request_id()
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

                        if src_amount.amount > Decimal(converted_amount):
                            transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                                    payer_email_address=src_email,
                                                                    payee_email_address=payee_email,
                                                                    amount_to_transfer_to_payee=amount_to_transfer,
                                                                    status="sent",
                                                                    payer_currency=src_currency,
                                                                    payee_currency=payee_currency,
                                                                    date=date.today())

                            transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                                    payer_email_address=payee_email,
                                                                    payee_email_address=src_email,
                                                                    amount_to_transfer_to_payee=converted_amount,
                                                                    status="received",
                                                                    payer_currency=payee_currency,
                                                                    payee_currency=src_currency,
                                                                    date=date.today())

                            src_amount.amount = src_amount.amount - Decimal(amount_to_transfer)
                            src_amount.save()

                            payee_amount.amount = payee_amount.amount + Decimal(converted_amount)
                            payee_amount.save()
                            is_tr_cmt = True


                        else:
                            messages.info(request, f"Insufficient Balance in your account.")
                    else:
                        converted_amount = amount_to_transfer
                        if src_amount.amount > Decimal(amount_to_transfer):
                            transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                                    payer_email_address=src_email,
                                                                    payee_email_address=payee_email,
                                                                    amount_to_transfer_to_payee=amount_to_transfer,
                                                                    status="sent",
                                                                    payer_currency=src_currency,
                                                                    payee_currency=payee_currency,
                                                                    date=date.today())

                            transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                                    payer_email_address=payee_email,
                                                                    payee_email_address=src_email,
                                                                    amount_to_transfer_to_payee=amount_to_transfer,
                                                                    status="received",
                                                                    payer_currency=payee_currency,
                                                                    payee_currency=src_currency,
                                                                    date=date.today())

                            src_amount.amount = src_amount.amount - Decimal(amount_to_transfer)
                            src_amount.save()

                            payee_amount.amount = payee_amount.amount + Decimal(converted_amount)
                            payee_amount.save()
                            is_tr_cmt = True
                        else:
                            messages.info(request, f"Insufficient Balance in your account.")

            except OperationalError:
                messages.info(request, f"Transfer operation is not possible now.")
            if is_tr_cmt==True:
                @transaction.on_commit
                def call_on_commit():
                    print("Transaction committed")
                    messages.success(request, "Amount transfer successful.")
        # transaction.on_commit()
        return render(request, "transactions/amount.html", {"src_email":src_email,
                                                            "src_currency":src_currency,
                                                            "request_id":request_id,
                                                            "src_amount": round(src_amount.amount,2),
                                                            "payee_email":payee_email,
                                                            "payee_currency":payee_currency,
                                                            "payee_amount": round(payee_amount.amount,2),
                                                            "tr_comt":"Transaction Committed"})
    else:
        form = MoneyTransferForm()
    return render(request, "transactions/amounttransfer.html", {"form": form})


@login_required(login_url='login')
def request_money_page(request):
    user_email = request.user.email
    try:
        queryset = Amount.objects.filter(~Q(email=request.user.email)).values_list("email", flat=True).distinct()
        beneficiaries = list(queryset)
        print("beneficiaries", beneficiaries)
    except Exception as e:
        beneficiaries = []

    # receive_payments_from_payers_format = [{'email': 'Ragini@gmail.com', 'amount': 1000, 'status': 'Pending'},
    #                                 {'email': 'Swapnil@gmail.com', 'amount': 2500, 'status': 'Received'}]


    # send_payments_to_users_format =[{'email': 'Ragini@gmail.com', 'amount': 1000, 'request_id': 2301},
    #                          {'email': 'Swapnil@gmail.com', 'amount': 2500, 'request_id': 5678}]

    try:
        money_requests = list(MoneyTransfer.objects.filter(Q(status="pending") | Q(status="accepted") | Q(status="rejected"),
                                                           payer_email_address=user_email))

        print("money_requests", money_requests)
    except Exception as e:
        money_requests = []

    try:
        send_queryset = MoneyTransfer.objects.filter(status="owed", payer_email_address=user_email).\
            values("request_id", "payee_email_address", "amount_to_transfer_to_payee")
        send_beneficiaries = [
            {'email': transfer['payee_email_address'], 'amount': transfer['amount_to_transfer_to_payee'], 'request_id': transfer['request_id']}
            for transfer in send_queryset
        ]

        print("send_beneficiaries", send_beneficiaries)
    except Exception as e:
        send_beneficiaries = []


    try:
        owed_money_requests = list(MoneyTransfer.objects.filter(Q(status="owed") | Q(status="paid") | Q(status="declined"),
                                                                payer_email_address=user_email))

        print("owed_money_requests", owed_money_requests)
    except Exception as e:
        owed_money_requests = []

    return render(request, "transactions/send_receive_requests.html",
                  {'beneficiaries': beneficiaries,
                    'money_requests': money_requests,
                   'send_beneficiaries': send_beneficiaries,
                    'owed_money_requests': owed_money_requests})


@csrf_protect
def request_money(request): # click on send button for requesting money to other user
    if request.method == 'POST':
        beneficiary_email = request.POST['beneficiary']
        amount = request.POST['amount']
        amount= Decimal(amount)
        user_email = request.user.email
        user_data = Amount.objects.filter(email=request.user.email).first()
        print(user_data)
        beneficiary_data = Amount.objects.filter(email=beneficiary_email).first()
        user_currency = user_data.primarycurrency
        beneficiary_currency = beneficiary_data.primarycurrency

        request_id = generate_request_id()

        if user_currency != beneficiary_currency:
            api_url = f"http://127.0.0.1:8000/conversion/{user_currency}/{beneficiary_currency}/{amount}/"
            response = requests.get(api_url)
            if response.status_code == 200:
                print(response.json())
                data = response.json()
                converted_amount = Decimal(data['converted_amount'])

                transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                        payer_email_address=user_email,
                                                        payee_email_address=beneficiary_email,
                                                        amount_to_transfer_to_payee=amount,
                                                        status="pending",
                                                        payer_currency=user_currency,
                                                        payee_currency=beneficiary_currency,
                                                        date=date.today())

                transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                        payer_email_address=beneficiary_email,
                                                        payee_email_address=user_email,
                                                        amount_to_transfer_to_payee=converted_amount,
                                                        status="owed",
                                                        payer_currency=beneficiary_currency,
                                                        payee_currency=user_currency,
                                                        date=date.today())
                messages.success(request, f"Request of amount {amount} Created for user {beneficiary_email} .")
            else:
                print('Error:', response.status_code)
        else:
            converted_amount = Decimal(amount)
            transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                    payer_email_address=user_email,
                                                    payee_email_address=beneficiary_email,
                                                    amount_to_transfer_to_payee=amount,
                                                    status="pending",
                                                    payer_currency=user_currency,
                                                    payee_currency=beneficiary_currency,
                                                    date=date.today())

                # user beneficiary se paise chah raha hai request kr rha hai use benef ko paise de do
            transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                    payer_email_address=beneficiary_email,
                                                    payee_email_address=user_email,
                                                    amount_to_transfer_to_payee=amount,
                                                    status="owed",
                                                    payer_currency=beneficiary_currency,
                                                    payee_currency=user_currency,
                                                    date=date.today())

            messages.success(request, f"Request of amount {amount} Created for user {beneficiary_email} .")
    try:
        user_email = request.user.email
        money_requests = list(MoneyTransfer.objects.filter(Q(status="pending") | Q(status="accepted") | Q(status="rejected"),
                            payer_email_address=user_email))

        print("money_requests", money_requests)
    except Exception as e:
        money_requests = []
    return render(request, "transactions/sendrequest.html", {'money_requests': money_requests})


@csrf_protect
def accept_reject_money_request(request):  # click on send button for requesting money to other user
    if request.method == 'POST':
        user_email = request.user.email
        data = request.POST.get('beneficiary')
        print(data)
        data_dict = eval(data)
        beneficiary_email = data_dict['email']
        user_data = Amount.objects.filter(email=user_email).first()
        beneficiary_data = Amount.objects.filter(email=beneficiary_email).first()
        amount = data_dict['amount']
        request_id = data_dict['request_id']
        user_currency = user_data.primarycurrency
        beneficiary_currency = beneficiary_data.primarycurrency
        accept_button = request.POST.get('acceptbutton')
        reject_button = request.POST.get('rejectbutton')

        print("user_email", user_email)
        print("user_currency", user_currency)
        print("beneficiary_email",beneficiary_email)
        print("beneficiary_currency",beneficiary_currency)
        print("amount", amount, "request_id", request_id)

        if accept_button is not None:
            if accept_button == "accept":
                print("accept block")
                try:
                    with transaction.atomic():
                        user_balance = Amount.objects.get(email=user_email)
                        money_request_user_data = MoneyTransfer.objects.get(request_id=request_id, status="owed", payer_email_address = user_email)

                        if user_balance.balance > money_request_user_data.amount_to_transfer_to_payee:
                            print("money_request_user_data Before modifying", money_request_user_data)
                            money_request_user_data.status = "paid"
                            money_request_user_data.save()  # Save the updated object back to the database

                            print("money_request_user_data After modifying", money_request_user_data)

                            print("user_balance Before modifying", user_balance)
                            user_balance.amount = user_balance.amount - money_request_user_data.amount_to_transfer_to_payee
                            user_balance.save()
                            print("user_balance After modifying", user_balance)

                            money_request_beneficiary_data = MoneyTransfer.objects.get(request_id=request_id, status="pending", payer_email_address = beneficiary_email)
                            print("money_request_beneficiary_data Before modifying", money_request_beneficiary_data)
                            # Update the status of the MoneyTransfer object to accepted
                            money_request_beneficiary_data.status = "accepted"
                            money_request_beneficiary_data.save()
                            print("money_request_beneficiary_data After modifying", money_request_beneficiary_data)
                            # Save the updated object back to the database
                            beneficiary_balance = Amount.objects.get(email=beneficiary_email)
                            print("beneficiary_balance Before modifying", beneficiary_balance)
                            beneficiary_balance.amount = beneficiary_balance.amount + money_request_beneficiary_data.amount_to_transfer_to_payee
                            beneficiary_balance.save()
                            print("beneficiary_balance After modifying", beneficiary_balance)
                        else:
                            messages.info(request, f"Insufficient Balance in your account.")
                except OperationalError:
                    messages.info(request, f"Money accept operation is not possible now.")
                @transaction.on_commit
                def call_on_commit():
                    print("Amount request accepted")
                    messages.success(request, "Amount transfer successful. Money request accepted.")
        elif reject_button is not None:
            if reject_button == "reject":
                print("reject block")
                try:
                    with transaction.atomic():
                        money_request_user_data = MoneyTransfer.objects.get(request_id=request_id, status="owed", payer_email_address = user_email)
                        print("money_request_user_data Before modifying", money_request_user_data)
                        money_request_user_data.status = "declined"
                        money_request_user_data.save()  # Save the updated object back to the database
                        print("money_request_user_data After modifying", money_request_user_data)

                        money_request_beneficiary_data = MoneyTransfer.objects.get(request_id=request_id, status="pending", payer_email_address = beneficiary_email)
                        print("money_request_beneficiary_data Before modifying", money_request_beneficiary_data)
                        # Update the status of the MoneyTransfer object to accepted
                        money_request_beneficiary_data.status = "rejected"
                        money_request_beneficiary_data.save()
                        print("money_request_beneficiary_data After modifying", money_request_beneficiary_data)

                except OperationalError:
                    messages.info(request, f"Money decline operation is not possible now.")
                @transaction.on_commit
                def call_on_commit():
                    print("Amount request declined")
                    messages.success(request, "Amount transfer did not happen. Money request declined.")
        else:
            print("None block")

    try:
        user_email = request.user.email
        owed_money_requests = list(MoneyTransfer.objects.filter(Q(status="owed") | Q(status="paid") | Q(status="declined"),
                                                                payer_email_address=user_email))
        print("owed_money_requests", owed_money_requests)

    except Exception as e:
        owed_money_requests = []
    return render(request, "transactions/owed_money_requests.html", {'owed_money_requests': owed_money_requests})


@login_required(login_url='login')
def get_all_payers(request):
    try:
        queryset = Amount.objects.filter(~Q(email=request.user.email)).values_list("email", flat=True).distinct()
        beneficiaries = list(queryset)
    except Exception as e:
        beneficiaries = []
    return render(request, "transactions/send_receive_requests.html", {'beneficiaries': beneficiaries})


@login_required(login_url='login')
def view_transactions(request):
    try:
        transactions = list(MoneyTransfer.objects.filter(payer_email_address=request.user.email))
    except Exception as e:
        transactions = []
    return render(request, "transactions/transaction_history_dynamic.html", {'transactions': transactions})


def generate_request_id():
    """
     this modified implementation, we check for the existence of a record with the same request_id
     and status='pending'. If such a record exists, we generate a new request_id until we find a unique one.
     Note that we are no longer using the pending_only parameter.
    """
    while True:
        request_id = random.randint(0, 9999)
        if not MoneyTransfer.objects.filter(request_id=request_id).exists() or \
                MoneyTransfer.objects.filter(request_id=request_id, status='pending').exists():
            return request_id
