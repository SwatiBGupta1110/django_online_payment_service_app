from django.shortcuts import render
import json
import requests
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Rate
from .serializers import RateSerializer
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, Http404
# from .serializers import AmountSerializer, MoneyTransferSerializer
# from transactions.models import Amount
# from transactions.models import MoneyTransfer

# Create your views here.

# path("conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/",
from rest_framework import generics

class CurrencyConverter(generics.ListCreateAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()

    def get(self, request, *args, **kwargs):
        currency1 = self.kwargs['currency1']
        currency2 = self.kwargs['currency2']
        amount_of_currency1 = float(self.kwargs['amount_of_currency1'])

        try:
            rate = float(Rate.objects.get(currency1=currency1, currency2=currency2).rate)
        except Rate.DoesNotExist:
            return Response({'error': 'One or both currencies not supported'}, status=status.HTTP_400_BAD_REQUEST)

        converted_amount = round(amount_of_currency1 * rate, 4)
        data = {'rate': rate, 'converted_amount': converted_amount}
        return Response(data)

#####################Correct###########
# class CurrencyConverter(generics.ListCreateAPIView, APIView):
#     serializer_class = RateSerializer
#
#     def get(self, request, currency1, currency2, amount_of_currency1):
#         # queryset = Rate.objects.all()
#         currency1 = self.kwargs['currency1']
#         currency2 = self.kwargs['currency2']
#         amount_of_currency1 = float(self.kwargs['amount_of_currency1'])
#         print("currency1", currency1)
#         print("currency2", currency2)
#         print("amount_of_currency1",amount_of_currency1)
#         try:
#             rate = float(Rate.objects.get(currency1=currency1, currency2=currency2).rate)
#             print("rate", rate)
#         except Rate.DoesNotExist:
#             return HttpResponseBadRequest('One or both currencies not supported', status=404)
#
#         converted_amount = round(amount_of_currency1 * rate, 4)
#         print("converted_amount", converted_amount)
#         data = {'rate': rate, 'converted_amount': converted_amount}
#         print(data)
#         response = JsonResponse(data, content_type='application/json')
#         return response

# from rest_framework.views import APIView
# from rest_framework.response import Response
#
# class MyView(APIView):
#     def get(self, request):
#         data = {'foo': 'bar'}
#         return Response(data)

def currency_converter_page(request):
    if request.method == 'GET':
        currency1 = request.GET.get('currency1', default="gbp")
        currency2 = request.GET.get('currency2', default="gbp")
        amount_of_currency1 = request.GET.get('amount_of_currency1',default=1000)

        api_url = f"http://127.0.0.1:8000/conversion/{currency1}/{currency2}/{amount_of_currency1}/"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            rate = data['rate']
            converted_amount = data['converted_amount']
            context = {
                'currency1': currency1,
                'amount_of_currency1': amount_of_currency1,
                'rate': rate,
                'currency2': currency2,
                'converted_amount': converted_amount,
            }
            return render(request, "convert_currency_api/currency_converter.html", context)
        else:
            error_message = response.text
            context = {'error_message': error_message}
            return render(request, "convert_currency_api/currency_converter.html", context)

#currency_converter("gbp","dollars",1000)
# def currency_converter(request, initial_currency="gbp",target_currency="gbp", amount=1000):
#     if request.method == "GET":
#         with open('register.json', 'r') as c:
#             conversion_data = json.load(c)
#         if initial_currency not in conversion_data or target_currency not in conversion_data[initial_currency]:
#             return HttpResponseBadRequest('One or both currencies not supported')
#         else:
#             rate = conversion_data[initial_currency][target_currency]
#             converted_amount = float(amount) * rate
#             converted_amount = round(converted_amount, 2)
#
#             data = {'rate': rate, 'converted_amount': converted_amount}
#             return JsonResponse(data)
#     else:
#         return HttpResponseBadRequest('Only GET requests are allowed.')

# class CurrencyConverter(generics.ListAPIView):
#     serializer_class = RateSerializer
#
#     def get_queryset(self):
#         currency1 = self.kwargs['currency1']
#         currency2 = self.kwargs['currency2']
#         amount = float(self.kwargs['amount_of_currency1'])
#
#         try:
#             rate = Rate.objects.get(currency1=currency1, currency2=currency2).rate
#         except Rate.DoesNotExist:
#             return HttpResponseBadRequest('One or both currencies not supported')
#
#         converted_amount = round(amount * rate, 2)
#         data = {'rate': rate, 'converted_amount': converted_amount}
#
#         return JsonResponse(data)




# class AmountList(generics.ListAPIView):
#     serializer_class = AmountSerializer
#
#     def get_queryset(self):
#         queryset = Amount.objects.all()
#         name = self.request.query_params.get('name')
#         if name is not None:
#             queryset = queryset.filter(username=name)
#         return queryset


"""
import requests

def convert_and_display_currency(request):
    # example usage: convert 100 USD to EUR
    url = 'http://localhost:8000/convert/USD/EUR/100/'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rate = data['rate']
        converted_amount = data['converted_amount']
        message = f'Conversion rate: {rate}, Converted amount: {converted_amount}'
    else:
        message = f'Error: {response.status_code} {response.reason}'
    return HttpResponse(message)

 # Use REST API to convert 1000 to the user's primary currency
            primary_currency = self.cleaned_data['primarycurrency']
            url = f'https://api.exchangerate-api.com/v4/latest/GBP'  # assuming base currency is GBP
            response = requests.get(url)
            data = response.json()
            rate = data['rates'][primary_currency]
            initial_amount = 1000 / rate
"""
