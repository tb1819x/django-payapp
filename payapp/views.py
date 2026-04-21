
"""
This module contains all of the business logic for the PayApp system.

It handles the following:
- User dashboard and admin views
- Sending and requesting payments
- Processing transactions between users
- Admin functionality
_ Currency conversion (REST)
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Account, Transaction, PaymentRequest
from .forms import sendMoneyForm, requestMoneyForm, RegisterAdminForm
from decimal import Decimal


@login_required
def dashboard(request):
    """
    Displays the logged-in user's dashboard, including account balance and currency.
    """
    
    account = Account.objects.get(user=request.user)

    return render(request, 'payapp/dashboard.html', {'account': account})


@login_required
def adminDashboard(request):
    """
    Displays the admin dashboard for staff users
    """

    adminUser = request.user

    return render(request, 'payapp/admindashboard.html', {'admin': adminUser})

    

@login_required
def send_money(request):
    """
    Handles send money between user

    - Validates sufficient balance and Recipients existence
    - Processes payment upon validation
    """
    sender_account = Account.objects.get(user=request.user)

    if request.method == 'POST':

        form = sendMoneyForm(request.POST)
        balance = sender_account.balance 

        if form.is_valid():
            money_to_send = form.cleaned_data['amount']

            if balance < money_to_send:
                form.add_error('amount', 'Insufficient funds')
                return render(request, 'payapp/send_money.html', {
                'form': form,
                'account': sender_account})
            
            #adding a try to avoid crashes
            try:
                recipient_user = User.objects.get(email=form.cleaned_data['recipient'])
                receiver_account = Account.objects.get(user=recipient_user)
            except User.DoesNotExist:
                form.add_error('recipient', 'Recipient does not exist')
                return render(request, 'payapp/send_money.html', {
                'form': form,
                'account': sender_account})
            
            process_payment(sender_account, receiver_account, money_to_send)
            return redirect('dashboard')
    else: 
        form = sendMoneyForm()

    return render(request, 'payapp/send_money.html', {
                'form': form,
                'account': sender_account})


@login_required
def request_money(request):
    """
    Handles creating a payment request from one user to another

    Validates user exists
    """
    requester_account = Account.objects.get(user=request.user)

    if request.method == 'POST':
        form = requestMoneyForm(request.POST)
        if form.is_valid():
            amount_requested = form.cleaned_data['amount']
            #search if the reciever of the request is actual user, wrapped in a try to avoid crashes
            try:
                recipient_email = User.objects.get(email=form.cleaned_data['recipient'])
            except User.DoesNotExist:
                form.add_error('recipient', 'Recipient does not exist')
                return render(request, 'payapp/request_money.html', {
                'form': form,
                'account': requester_account})
            #if reciever exists, create Pay request
            paymentRequest = PaymentRequest(
                requester=request.user,
                recipient=recipient_email,
                amount=amount_requested
            )
            paymentRequest.save()
            return redirect('dashboard')
    else: 
        form = requestMoneyForm()

    return render(request, 'payapp/request_money.html', {
                'form': form,
                'account': requester_account})  

@login_required
def payment_requests(request):

    """
    Displays all payment requests for the logged-in user

    This includes incoming requests and Requests sent by the user
    """

    #filter grabs many objects django instead of one.
    incoming_requests = PaymentRequest.objects.filter(recipient=request.user, status="pending")
    sent_requests = PaymentRequest.objects.filter(requester=request.user)

    return render(request, 'payapp/payment_requests.html', {
        'incoming_requests': incoming_requests,
        'sent_requests': sent_requests
    })

@login_required
def handle_request(request, request_id):
    """
    Handles accepting or rejecting payment request

    validates user balance upon acceptance and processes the payment using
    helper function process_payment()

    updates status if request is rejected
    """

    action = request.POST.get('action')

    #retrieves payment request or returns 404 object is not found istead of try 
    paymentRequest = get_object_or_404(
        PaymentRequest,
        id=request_id,
        recipient=request.user
    )
    if action == 'accept':
        paymentRequest.status = 'accepted'
        paymentRequest.save()

        sender_account = Account.objects.get(user=request.user)
        balance = sender_account.balance
        recipient_account =  Account.objects.get(user=paymentRequest.requester)
        amount_due = paymentRequest.amount

        if balance < amount_due:
            messages.error(request, "Insufficient funds available")
            return redirect('payment_requests')
        
        process_payment(sender_account, recipient_account, amount_due) 
        messages.success(request, "Payment sent successfully")
        return redirect('payment_requests') 
         
    else:
        paymentRequest.status = 'rejected'
        paymentRequest.save()
        messages.success(request, "Request Rejected")
        return redirect('payment_requests')

#helper function
def process_payment(senderAccount, recipientAccount, amount):
            """
            Processes a payment between two accounts.

            converts currency
            deducts amount from user and adds coverted funds to recpient
            creates a record of the transaction
            """
            sender_currency = senderAccount.currency
            recipient_currency = recipientAccount.currency
            amount_converted = convert_currency(amount, sender_currency, recipient_currency)

            senderAccount.balance -= Decimal(amount)
            recipientAccount.balance += Decimal(amount_converted)
            senderAccount.save()
            recipientAccount.save()

            transaction = Transaction(
                        sender=senderAccount.user,
                        receiver=recipientAccount.user,
                        amount=amount,
                    )
            transaction.save()

@login_required
def transactions(request):
    """
    Display all previous transctions for logged in user

    -incoming payments and outgoing payments
    """

    #filter grabs many objects django instead of one.
    money_in_transactions = Transaction.objects.filter(receiver=request.user)
    money_out_transactions = Transaction.objects.filter(sender=request.user)
    return render(request, 'payapp/transactions.html', {
        'money_in_transactions': money_in_transactions,
        'money_out_transactions': money_out_transactions
    })

@login_required
def userAccounts(request):
    """
    This allows Admins to view all user accounts

    - redirects user to dashboard if not admin
    """
    #Restrict access to staff users only
    if not request.user.is_staff:
        return redirect('dashboard')
    
    user_accounts = Account.objects.all()
    admin_users = User.objects.filter(is_staff=True)

    return render(request, 'payapp/admin_accounts_view.html', {
        'user_accounts': user_accounts,
        'admin_accounts': admin_users
    })

@login_required
def userTransactions(request):
    """
    Admin view to display all transactions

    - only accessible to staff accounts
    """
    if not request.user.is_staff:
        return redirect('dashboard')
    
    all_transactions = Transaction.objects.all()

    return render(request, 'payapp/admin_transactions_view.html', {
        'transactions': all_transactions
    })

@login_required
def register_new_admin(request):
    """
    Allows Admin to register a new admin

    -creates new user with admin privileges 
    """
    
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterAdminForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            
            return redirect('admin_dashboard')
    else:
        form = RegisterAdminForm()
    
    return render(request, 'payapp/register_admin.html', {'form': form})

def convert_currency(amount, original_currency, convert_to_currency):
    """
    Converts an amount between currencies using predefined exchange rates
    """
    amount = float(amount)

    rates = {
        'USD': {'GBP': 0.77, 'EUR': 0.88},
        'GBP': {'USD': 1.3, 'EUR': 1.15},
        'EUR': {'GBP': 0.87, 'USD': 1.14}
    }

    if original_currency == convert_to_currency:
        return amount
    try: 
        rate = rates[original_currency][convert_to_currency]
        return round(amount * rate, 2)
    except KeyError:
        return None


def conversion(request, original_currency, convert_to_currency, amount):
    """
    Rest Api endpoint currency conversion

    Returns:
    - Converted amount in Json format
    _ Error reponse if currency is invalid
    """
    result = convert_currency(amount, original_currency, convert_to_currency)

    if result is None: 
        return JsonResponse({
            'error': 'Invalid currency'
        }, status=400)
    return JsonResponse({
        'from': original_currency,
        'to': convert_to_currency,
        'original_amount': float(amount),
        'converted_amount': result
    })