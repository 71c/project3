from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.urls import include, path


urlpatterns = [
    path("", views.menu, name="menu"),
    path("dish/", views.dish, name="dish")
]
