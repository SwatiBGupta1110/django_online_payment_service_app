"""
URL configuration for webapps2023 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

#http://127.0.0.1:8000/admin/ --> Admin Page

from django.contrib import admin
from django.urls import path, include
from home import views as home_views
from register import views as register_views
from convert_currency_api.views import CurrencyConverter
from convert_currency_api import views as currencyconverter_views
from transactions import views as transactions_views


admin.site.site_header = "Payzapp Admin"
admin.site.site_title = "Payzapp Admin Portal"
admin.site.index_title = "Welcome to Payzapp"



"""
Name: Badri Gupta
username: badrijagannathgupta
email: badri@gmail.com
Password: seemagupta05
Currency : GBP

Name: Seema Gupta
username: seemabadrigupta
email: seema@gmail.com
Password: mybirthday0501
Currency : GBP

Name: Akshay Gupta
username: akshaybadrigupta
email: akshay@gmail.com
Password: golu200223
Currency : Dollars

Name: Krishna Vasudev
email: krishna@gmail.com
username: kanha1111
password: radha2222
currency: INR
"""


urlpatterns = [
    path("admin/", admin.site.urls),  #Django admin site page path
    path("", home_views.index, name="home"),  # Home page path
    path("", include("home.urls", namespace="home")), # Imports endpoint for about and contact page
    path("register_user/", include("register.urls", namespace="register")), # Endpoint for register page
    path("login/", register_views.login_user, name="login"), #Endpoint for login page
    path("logout/", register_views.logout_user, name="logout"),#Endpoint for logout page
    path("dashboard/", register_views.dashboard_page, name="dashboard"),#Endpoint for dashboard page
    path("conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/", CurrencyConverter.as_view(),
         name="currencyconverter"), #Currency conversion api
    path("conversionpage/", currencyconverter_views.currency_converter_page, name="currencyconverterpage"), #Endpoint for currency conversion page
    path("amounttransfer/", transactions_views.amount_transfer, name="amounttransfer"),#Endpoint for amount transfer page
    path("getpayerlist/", transactions_views.get_all_payers, name="getpayerlist"), #Endpoint for getting all payers list
    path("requestmoneypage/", transactions_views.request_money_page, name="requestmoneypage"),#Endpoint for loading request money page data
    path("request_money/", transactions_views.request_money, name="requestmoney"),#Endpoint for requesting money
    path("accept_reject_money_request/", transactions_views.accept_reject_money_request, name="acceptrejectmoneyrequest"),#Endpoint for accept reject request
    path("view_transactions/", transactions_views.view_transactions, name="viewtransactions"), # endpoint for all transactions
]