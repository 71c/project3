from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .models import *

# Create your views here.
def menu(request):

    menu = {
        menu_section: {
            'dishes': menu_section.dishes_included.all(),
            'there_are_one_price_dishes': any(dish.price != None for dish in menu_section.dishes_included.all()),
            'topping_price_is_included': menu_section.topping_price_is_included,
        }
        for menu_section in MenuSection.objects.all()
    }

    variables = {
        'menu': menu.items(),
    }
    return render(request, 'orders/menu.html', variables)


def dish(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        dish = Dish.objects.get(id=dish_id)

        item = Item.create(dish)
        sizes_and_prices = item.get_size_dict()
        there_is_one_size = len(sizes_and_prices) == 1

        a = {
            'dish_name': item.dish.name,

            'sizes_and_prices': sizes_and_prices,
            'sizes_and_prices_items': sizes_and_prices.items(),
            'there_is_one_size': there_is_one_size,

            'global_available_toppings': item.get_global_available_toppings(),
            'local_available_toppings': item.get_local_available_toppings(),

            'min_global_toppings': item.dish.min_global_toppings,
            'max_global_toppings': item.dish.max_global_toppings,
            'min_local_toppings': item.dish.min_local_toppings,
            'max_local_toppings': item.dish.max_local_toppings,
            'topping_price_is_included': item.dish.menu_section.topping_price_is_included
        }

        min_max_and_lists = [
            (a['min_global_toppings'], a['max_global_toppings'], a['global_available_toppings'], ''),
            (a['min_local_toppings'], a['max_local_toppings'], a['local_available_toppings'], 'extra ')
        ]

        print(type(a['sizes_and_prices_items']))
        single_price = list(a['sizes_and_prices_items'])[0][1]

        a['min_max_and_lists'] = min_max_and_lists
        a['single_price'] = single_price

        return render(request, 'orders/dish.html', a)

def add_to_cart(request):
    print(request.POST)