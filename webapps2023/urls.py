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
email: badrigupta@gmail.com
username: badrijagannath
Password: seemagupta05
Currency : GBP

Name: Seema Gupta
email: seema@gmail.com
username: seemabadrigupta
Password: husband@21
Currency : GBP

Name: Akshay Gupta
email: akshay@gmail.com
username: akshay23
Password: golu200223
Currency : Dollars

Name: Krishna Vasudev
email: krishna@gmail.com
username: kanha1111
password: radha2222
currency: INR
"""


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_views.index, name="home"),
    path("", include("home.urls", namespace="home")),
    path("register_user/", include("register.urls", namespace="register")),
    # path("register_user/", register_views.register_user, name="register_user"),
    path("login/", register_views.login_user, name="login"),
    path("logout/", register_views.logout_user, name="logout"),
    path("dashboard/", register_views.dashboard_page, name="dashboard"),
    path("conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/", CurrencyConverter.as_view(),
         name="currencyconverter"),
    path("conversionpage/", currencyconverter_views.currency_converter_page, name="currencyconverterpage"),
    path("amounttransfer/", transactions_views.amount_transfer, name="amounttransfer"),
    path("getpayerlist/", transactions_views.get_all_payers, name="getpayerlist"),
    # path("example/", MyView.as_view(),
    #      name="currencyconverter"),
]