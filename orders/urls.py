from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.urls import include, path


urlpatterns = [
    path("", views.menu, name="menu"),
    path("dish/", views.dish, name="dish"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("added_to_cart/", views.added_to_cart, name="added_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("order/", views.order, name="order"),
    path("order_placed/", views.order_placed, name="order_placed")
]
