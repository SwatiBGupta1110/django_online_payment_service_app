from .forms import RegisterUser
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        register_user=RegisterUser(request.POST)
        if register_user.is_valid():
            register_user.save()       #<-- saving the form to the database
            return redirect("login")
        messages.error(request, register_user.errors)
    register_user=RegisterUser()
    return render(request, "register/register.html", {"register_user": register_user})


@csrf_exempt
def login_user(request):
    if request.method =="POST": #check if form is posted
        form = AuthenticationForm(request, request.POST)   # Initialize Authenticate form function
        if form.is_valid():  #checks form is valid
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None: # If user exists in database
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return render(request, "register/dashboard.html")              # return user object
                # backend authenticated the user credentials
            else:
                messages.error(request, "Invalid Username or password") # backend did not authenticated the user credentials
        else:
            messages.error(request, "Form is invalid.") #When form is not valid
    form = AuthenticationForm()
    # Set the size of the username and password fields
    return render(request,"register/login.html", {"login_user":form})   # return blank login form

#Old Version same as commenstore
# def logout_user(request):
#     logout(request)
#     userForm=AuthenticationForm()
#     messages.success(request, "You have successfully logged out.")
#     return render(request, "register/login.html", {"login_user": userForm})


def logout_user(request):
    logout(request)
    userForm=AuthenticationForm()
    messages.success(request, "You have successfully logged out.")
    # return render(request, "register/login.html", {"login_user": userForm})
    # return redirect("login", {"login_user": userForm})
    return redirect("login")


@login_required(login_url='login')
def dashboard_page(request):
    return render(request, 'register/dashboard.html')