from django.contrib import admin
from django.urls import path, include
from register import views

app_name = 'register'

urlpatterns = [
    path("", views.register_user, name="register_user"),
    # path("login/", views.login_user, name="login"),
    # path("logout/", views.logout_user, name="logout"),
]