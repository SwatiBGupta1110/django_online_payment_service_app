from .forms import RegisterUser
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
# Create your views here.
from transactions.models import Amount

currency_dict = {'gbp': 'GBP', 'usd': 'USD', 'euros': 'EUROS', 'inr': 'INR'}

"""
This view function saves web app from csrf attack.
This function is responsible for getting the POST data safely once user registers
and saving the user then redirecting to login page.
otherwise it returns register form to user if it is a GET request.
"""
@csrf_protect
def register_user(request):
    if request.method == 'POST':
        register_user=RegisterUser(request.POST)
        if register_user.is_valid():
            register_user.save()       #<-- saving the form to the database
            return redirect("login")
        messages.error(request, register_user.errors)
    register_user=RegisterUser()
    return render(request, "register/register.html", {"register_user": register_user})


"""
This view function is saved from csrf attack.
This function is responsible for getting the POST data from login page,
getting the cleaned username and password authenticating user and displaying user currency and amount to dashboard page.
and if user is authenticated user then redirecting to dashboard page.
otherwise it returns login form to user if it is a GET request.
It also displays a message info for guiding user properly based on his action
"""
@csrf_protect
def login_user(request):
    if request.method =="POST": #check if form is posted
        form = AuthenticationForm(request, request.POST)   # Initializing Authenticate form function
        if form.is_valid():  #checks form is valid
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None: # If user exists in database
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                user_data = Amount.objects.filter(email=request.user.email).first()
                print(user_data)
                user_amount = round(user_data.amount, 2)
                user_currency = currency_dict[user_data.primarycurrency]
                return render(request, "register/dashboard.html",{"user_amount":user_amount,
                                                                  "user_currency":user_currency})
                # backend authenticated the user credentials
            else:
                messages.error(request, "Invalid Username or password") # backend did not authenticated the user credentials
        else:
            messages.error(request, "Form is invalid.") #When form is not valid
    form = AuthenticationForm()
    # Set the size of the username and password fields
    return render(request,"register/login.html", {"login_user":form})   # return blank login form


"""
The url implemented for this function requires user to be an authenticated logged in user
This function is responsible for loggging out user safely and redirecting to login page back.
"""
@login_required(login_url='login')
def logout_user(request):
    logout(request)
    userForm=AuthenticationForm()
    messages.success(request, "You have successfully logged out.")
    return redirect("login")


"""
This view function can only be accessed by users who are logged in autheticated user.
It is responsible for rendering dashboard page to users where they can use different functionalities of this web app.
It also renders amount and currency to dashboard page.
"""
@login_required(login_url='login')
def dashboard_page(request):
    user_data = Amount.objects.filter(email=request.user.email).first()
    print(user_data)
    user_amount = round(user_data.amount, 2)
    user_currency = currency_dict[user_data.primarycurrency]
    return render(request, 'register/dashboard.html', {"user_amount":user_amount,
                                                      "user_currency":user_currency})