"""
This module defines all URL routes for the authentication component of the PayApp system

Maps urls to corresponding view functions
"""
from django.urls import path
from .views import register, login_view, logout_view

urlpatterns = [
   path('register/', register, name="register"), 
   path('login/', login_view, name="login"),
   path('logout/', logout_view, name="logout")
]