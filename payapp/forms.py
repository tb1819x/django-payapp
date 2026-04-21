"""
This module is creates all forms for the PayApp system
Including
-send money
-request money
-register new admins
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class sendMoneyForm(forms.Form):
    """
    Form for sending money between users

    uses django's built in form system to validate
    - Recipients email
    -Amount
    -optional message
    """
    recipient = forms.EmailField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2,  min_value=0.01)
    message = forms.CharField(widget=forms.Textarea, required=False)

class requestMoneyForm(forms.Form):
    """
    Form for requesting money between users

    validates:
    - Recipient email
    - Requested amount
    """
    recipient = forms.EmailField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2,  min_value=0.01)

class RegisterAdminForm(UserCreationForm):
    """
    Form for registering new admin users using Django's built in authentication system 
    """
 
    class Meta:
        model = User
        fields = ['username', 'password1', "password2"]

