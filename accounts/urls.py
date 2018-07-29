from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.urls import include, path

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    url(r'^activate/account/$', views.activate_account, name='activate')
]