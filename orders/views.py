from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .models import *
from accounts.models import Customer

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
        print({key: sizes_and_prices[key] for key in sizes_and_prices})
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
            'topping_price_is_included': item.dish.menu_section.topping_price_is_included,

            'dish_id': dish.id
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
    post = request.POST

    size = post.get('size')
    topping_ids = post.get('toppings')
    dish_id = post.get('dish_id')

    dish = Dish.objects.get(id=dish_id)
    item = Item.create(dish)
    item.save()
    item.size = size

    if topping_ids != None:
        for topping in topping_ids:
            # print(topping)
            item.toppings.add(Topping.objects.get(id=topping))

    current_customer = request.user.customer
    current_customer.cart.add(item)

    item.save()

    return redirect('added_to_cart')

def added_to_cart(request):
    return render(request, 'orders/added_to_cart.html')

def cart(request):
    current_customer = request.user.customer
    customer_cart = current_customer.cart.all()
    print(customer_cart)

    dishes_and_prices = [(f"{item.dish.menu_section}: {item.dish.name}", item.calculate_price()) for item in customer_cart]
    dishes_and_prices = [a for a in dishes_and_prices if a[1] != None]
    return render(request, 'orders/cart.html', {
        'cart': dishes_and_prices,
        'total': sum([a[1] for a in dishes_and_prices]),
        'empty_cart': len(dishes_and_prices) == 0
    })
