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

"""
This function is responsible for handling the logic related to amounttransfer endpoint.
It is protected from csrf attacks and transaction happens only if it is atomic.
if request is POST, data is extracted from request and cleaned.
Unique request id is created when amount is transferred to other user.
Once this is done, user currency and payee currency is checked it is same then 
conversion get api is not called, if it not same api is called which converts the amount.
Transfer happens only if user is having account balance greater than the amount he needs to transfer
and data is saved on MoneyTransfer model where status is updated as send for payer
and received for payee, it will be an atomic transaction and messages are displayed if user have insufficient balance
transfer does not take place in that case.
"""
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
                    # Checking is currency is not same, conversion api is called
                    if src_currency != payee_currency:
                        api_url = f"http://127.0.0.1:8000/conversion/{src_currency}/{payee_currency}/{amount_to_transfer}/"
                        response = requests.get(api_url)
                        if response.status_code == 200:
                            print(response.json())
                            data = response.json()
                            converted_amount = data['converted_amount']
                        else:
                            print('Error:', response.status_code)

                        # User Amount balance should be greater than amount he wants to transfer
                        if src_amount.amount > Decimal(converted_amount):

                            # creating record in MoneyTransfer model and updating status as sent
                            transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                                    payer_email_address=src_email,
                                                                    payee_email_address=payee_email,
                                                                    amount_to_transfer_to_payee=amount_to_transfer,
                                                                    status="sent",
                                                                    payer_currency=src_currency,
                                                                    payee_currency=payee_currency,
                                                                    date=date.today())
                            # creating record in MoneyTransfer model and updating status as received
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
                        # User Amount balance should be greater than amount he wants to transfer
                        if src_amount.amount > Decimal(amount_to_transfer):
                            # creating record in MoneyTransfer model and updating status as sent
                            transfer = MoneyTransfer.objects.create(request_id=request_id,
                                                                    payer_email_address=src_email,
                                                                    payee_email_address=payee_email,
                                                                    amount_to_transfer_to_payee=amount_to_transfer,
                                                                    status="sent",
                                                                    payer_currency=src_currency,
                                                                    payee_currency=payee_currency,
                                                                    date=date.today())

                            # creating record in MoneyTransfer model and updating status as received
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
                                                            "amount_transferred_to_payee": round(amount_to_transfer,2),
                                                            "tr_comt":"Transaction Committed"})
    else:
        form = MoneyTransferForm()
    return render(request, "transactions/amounttransfer.html", {"form": form})


"""
This function is responsible for loading all the data for creating money request or accept/decline money request
It is responsible for passing information for request payment and accept/ decline payment table for user
and for passing information loaded in drop down.
"""
@login_required(login_url='login')
def request_money_page(request):
    user_email = request.user.email
    try:
        # Query filters out all the other users email address existing in system except users address
        # to be displayed in beneficiaries drop down
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
        # Query filters out all the data for accepted, pending and rejected payment for user
        money_requests = list(MoneyTransfer.objects.filter(Q(status="pending") | Q(status="accepted") | Q(status="rejected"),
                                                           payer_email_address=user_email))

        print("money_requests", money_requests)
    except Exception as e:
        money_requests = []

    try:
        #Query filters out received request where status is owed and extract values "request_id", "payee_email_address", "amount_to_transfer_to_payee"
        # converts it in a below format to be used by frontend html page
        # to be displayed in send_beneficiaries drop down
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
        # Query filters out all the data for request where status is owed, paid, declined for user
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


"""
This view function is safe from csrf attack and extracts the data from request if it is a POSt request
otherwise renders sendrequest, It generates a new request id in this case and call converion api
for converting the amount if user currency and the person whom he is requesting currency is not same.
once converted amount is received data is stored in MoneyTransfer with status as pending for the who requested,
and owed for the user for whom request is created.
It also renders money_requests in which queries data for related html page if it is a pending, accepted or rejected request
"""
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
        # Query for filtering data for html page if it is a pending, accepted or rejected request
        money_requests = list(MoneyTransfer.objects.filter(Q(status="pending") | Q(status="accepted") | Q(status="rejected"),
                            payer_email_address=user_email))

        print("money_requests", money_requests)
    except Exception as e:
        money_requests = []
    return render(request, "transactions/sendrequest.html", {'money_requests': money_requests})


"""
This view function is safe from csrf attack and extracts the data from request if it is a POSt request
otherwise renders owed_money_requests, It checks the value of button passed from frontend
and gets inside the related block of that value.
If it is a accept button , it goes inside accept block and then if user amount is greater than his balance then 
money transfer happens and amount is deducted from payer account and record is created in MoneyTransfer model,
with status as accepted.
If it is a reject button, simply status is updated as declined for payer and rejected for one who requested payment.
Transfer happens only it is atomic, otherwise not, relevant messages are displayed to
user in both the sceneario of accept and reject request.
"""
@csrf_protect
def accept_reject_money_request(request):
    # Once user clicks on send button for sending money for received requests this view function is called
    # endpoint accept_reject_money_request/
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

                        if user_balance.amount > money_request_user_data.amount_to_transfer_to_payee:
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
    """
    get_all_payers can be seen only by authenticated logged in user and
    is responsible for quering all the email id except users email id flattening it and
    returning unique record to be displayed in beneficiaries
    Then rendering those beneficiaries to send_receive_requests.html
    """
    try:
        queryset = Amount.objects.filter(~Q(email=request.user.email)).values_list("email", flat=True).distinct()
        beneficiaries = list(queryset)
    except Exception as e:
        beneficiaries = []
    return render(request, "transactions/send_receive_requests.html", {'beneficiaries': beneficiaries})


@login_required(login_url='login')
def view_transactions(request):
    """
    view_transactions can be seen only by authenticated logged in user and
    is responsible for first quering all the transactions related to logged in user
    and then rendering those transactions to transaction_history.html
    """
    try:
        transactions = list(MoneyTransfer.objects.filter(payer_email_address=request.user.email))
    except Exception as e:
        transactions = []
    return render(request, "transactions/transaction_history.html", {'transactions': transactions})



def generate_request_id():
    """
     This function is responsible for generating request id or in general terms transaction id.
     We check if there is any existing record with the same request_id
     and status='pending'. If there is any such record we generate a new request id.
    """
    while True:
        request_id = random.randint(0, 9999)
        if not MoneyTransfer.objects.filter(request_id=request_id).exists() or \
                MoneyTransfer.objects.filter(request_id=request_id, status='pending').exists():
            return request_id
