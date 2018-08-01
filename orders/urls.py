from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.urls import include, path


urlpatterns = [
    path("", views.menu, name="menu"),
    path("dish/", views.render_dish, name="render_dish"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("added_to_cart/", views.added_to_cart, name="added_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("place_order/", views.place_order, name="place_order"),
    path("order_placed/", views.order_placed, name="order_placed"),
    path('admin_view_orders/', views.admin_view_orders, name='admin_view_orders'),
    path('order/', views.view_order, name="view_order")
]
