"""
This module defines all URL routes for the PayApp application

Maps urls to corresponding view functions
"""
from django.urls import path
from .views import dashboard, send_money, request_money, payment_requests, handle_request, transactions, userAccounts, userTransactions, adminDashboard, register_new_admin, conversion

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('send_money/', send_money, name='send_money'),
    path('request_money/', request_money, name='request_money'),
    path('payment_requests/', payment_requests, name='payment_requests'),
    path('payment_requests/<int:request_id>/handle/', handle_request, name='handle_request'),
    path('transactions/', transactions, name='transactions'),
    path('admindashboard/', adminDashboard, name='admin_dashboard'),
    path('admin_accounts_view/', userAccounts, name='admin_accounts_view'),
    path('admin_transactions_view/', userTransactions, name='admin_transactions_view'),
    path('register_new_admin/', register_new_admin, name='register_new_admin'),
    path('conversion/<str:original_currency>/<str:convert_to_currency>/<str:amount>/', conversion, name='conversion'),
]

