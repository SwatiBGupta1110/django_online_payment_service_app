from django.urls import path
from . import views

# This url imports the views responsible for money transfer
urlpatterns = [
    path('', views.amount_transfer, name='amount_transfer'),
]