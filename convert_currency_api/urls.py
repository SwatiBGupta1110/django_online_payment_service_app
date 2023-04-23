from django.contrib import admin
from django.urls import path, include
from convert_currency_api.views import CurrencyConverter

app_name = 'convert_currency_api'
# path('comment/<int:pk>', CommentDetail.as_view()),

"""
This is a get api which has format as  https://127.0.0.1:8000/conversion/euros/inr/80/ .
where currency1 and currency2 are sting and amount_of_currency1 is a float amount.
"""
urlpatterns = [
    # baseURL/conversion/{currency1}/{currency2}/{amount_of_currency1}
    #http://127.0.0.1:8000/conversion/euros/inr/80/
    path("conversion/<str:currency1>/<str:currency2>/<float:amount_of_currency1>/",  CurrencyConverter.as_view(), name="currency_converter"),
]

#http://localhost:8000/conversion/usd/euros/100
