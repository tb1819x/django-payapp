"""
This module contains all of the logic for the authentication part of the PayApp system.

It handles the following:
- Register
- Login
- Logout
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm 
from payapp.models import Account
from payapp.views import convert_currency



def register(request):
    """
    This handles user registration

    Displays form, registers user on submission and redirects to login upon saving
    """

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            currency = form.cleaned_data['currency']
            
            starting_balance = convert_currency(500, 'GBP', currency)
            
            Account.objects.create(
                user=user,
                balance=starting_balance,
                currency=currency 
            )
            return redirect('login')
    else:
        form = RegistrationForm()
    
    return render(request, 'register/register.html', {'form': form})

def login_view(request):
    """
    Handles user login

    displays login form, validates user on submission and redirects to logged in page
    """

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user  = authenticate(request, username=username, password=password)

        if user is not None: 
            login(request, user)
            if request.user.is_staff:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            form = AuthenticationForm()

    else:
        form = AuthenticationForm()
    return render(request, 'register/login.html', {'form': form, 'title': 'login'})


def logout_view(request):
    """
    logs out user and redirects user to the login page
    """

    logout(request)
    return redirect('login')




