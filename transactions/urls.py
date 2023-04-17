from django.urls import path
from . import views

urlpatterns = [
    path('', views.amount_transfer, name='amount_transfer'),
]