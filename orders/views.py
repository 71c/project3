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
            'items': list(menu_section.dishes_included.all()) + list(menu_section.toppings_included.all()),
            'toppings': list(menu_section.toppings_included.all()),
            'dishes': list(menu_section.dishes_included.all()),
            'there_are_one_price_dishes': any(dish.price != None for dish in menu_section.dishes_included.all()),
            'topping_price_is_included': menu_section.topping_price_is_included,
            'there_are_only_toppings': len(menu_section.dishes_included.all()) == 0
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
        return render(request, 'orders/dish.html', {'dish': dish, 'available_toppings': dish.get_available_toppings().all(), 'topping_range': range(dish.max_toppings)})

