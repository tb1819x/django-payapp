"""
This module is creates form for the authentication part of the PayApp system
Including:
-Registration
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    """
    Form for registering new users using Django's built in authentication system 
    """

    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(
        choices=[
            ('GBP', 'GBP'),
            ('USD', 'USD'),
            ('EUR', 'EUR')
        ]
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', "password2"]

