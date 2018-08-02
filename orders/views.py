from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.utils.timezone import now

from django.contrib import messages

from accounts.models import *

# Create your views here.
def menu(request):

    menu = {
        menu_section: {
            'dishes': menu_section.dish_set.all(),
            'there_are_one_price_dishes': any(dish.price != None for dish in menu_section.dish_set.all()),
            'topping_price_is_included': menu_section.topping_price_is_included,
        }
        for menu_section in MenuSection.objects.all()
    }

    variables = {
        'menu': menu.items(),
    }
    return render(request, 'orders/menu.html', variables)


def render_dish(request):
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
            'topping_price_is_included': item.dish.menu_section.topping_price_is_included,

            'dish_id': dish.id
        }

        min_max_and_lists = [
            (a['min_global_toppings'], a['max_global_toppings'], a['global_available_toppings'], 'global'),
            (a['min_local_toppings'], a['max_local_toppings'], a['local_available_toppings'], 'local')
        ]

        single_price = list(a['sizes_and_prices_items'])[0][1]

        a['min_max_and_lists'] = min_max_and_lists
        a['single_price'] = single_price

        errors = request.POST.get('errors')
        if errors != None:
            a['errors'] = errors

        return render(request, 'orders/dish.html', a)


def add_to_cart(request):
    errors = []

    post = request.POST

    if not request.user.is_authenticated:
        errors += ["You're not logged in!"]

    size = post.get('size')
    size_selected = size != None
    if not size_selected:
        errors += ['You need to pick a size']

    dish_id = post.get('dish_id')
    dish = Dish.objects.get(id=dish_id)
    item = Item.create(dish)
    item.size = size

    topping_ids = post.getlist('toppings')
    if topping_ids != None:
        topping_ids = [id_and_type.split(',') for id_and_type in topping_ids]
        global_topping_ids = [topping_id for topping_id, topping_type in topping_ids if topping_type == 'global']
        local_topping_ids = [topping_id for topping_id, topping_type in topping_ids if topping_type == 'local']

        global_toppings_in_range = dish.min_global_toppings <= len(global_topping_ids) <= dish.max_global_toppings
        local_toppings_in_range = dish.min_local_toppings <= len(local_topping_ids) <= dish.max_local_toppings

        if not global_toppings_in_range:
            if dish.min_global_toppings > len(global_topping_ids):
                errors += ['not enough toppings']
            else:
                errors += ['too many toppings']
        if not local_toppings_in_range:
            if dish.min_local_toppings > len(local_topping_ids):
                errors += ['not enough extra toppings']
            else:
                errors += ['too many extra toppings']

        if len(errors) > 0:
            dish_data = {
              'dish_id': dish_id,
              'errors': errors
            }
            request.POST = dish_data
            return render_dish(request)

        item.save()

        if global_topping_ids != None:
            for topping_id in global_topping_ids:
                item.toppings.add(Topping.objects.get(id=topping_id))
        if local_topping_ids != None:
            for topping_id in local_topping_ids:
                item.toppings.add(Topping.objects.get(id=topping_id))



    current_customer = request.user.customer

    if current_customer.cart == None:
        order = Order()
        order.save()
        current_customer.cart = order
        current_customer.save()

    item.order = current_customer.cart
    item.save()

    current_customer.cart.update_price()
    current_customer.cart.save()

    return redirect('added_to_cart')

def added_to_cart(request):
    return render(request, 'orders/added_to_cart.html')

def cart(request):
    current_customer = request.user.customer
    if current_customer.cart == None:
        dishes_and_prices = []
    # else:
        # customer_cart = current_customer.cart.item_set.all()
        # dishes_and_prices = [(f"{item.dish.menu_section}: {item.dish.name}", item.calculate_price()) for item in customer_cart]
        # dishes_and_prices = [a for a in dishes_and_prices if a[1] != None]

    # return render(request, 'orders/cart.html', {
    #     'cart': dishes_and_prices,
    #     'total': sum([a[1] for a in dishes_and_prices]),
    #     'empty_cart': len(dishes_and_prices) == 0
    # })

    cart = current_customer.cart

    if cart == None:
        cart_items = []
    else:
        cart_items = cart.item_set.all()


    empty_cart = len(cart_items) == 0

    variables = {
        'empty_cart': empty_cart
    }
    if not empty_cart:
        variables['total'] = cart.price
        variables['items'] = [
            {
                'dish': item.dish,
                'size': item.size,
                'toppings': ', '.join(topping.name for topping in item.toppings.all()),
                'price': item.calculate_price()
            }
            for item in cart_items
        ]
    return render(request, 'orders/cart.html', variables)


def place_order(request):
    customer = request.user.customer

    # reference the Order to the Customer
    customer.cart.customer = customer
    # set the date that the order was placed
    customer.cart.date = now()
    customer.cart.placed = True
    customer.cart.update_price()

    customer.cart.save()

    # clear cart
    customer.cart = None
    customer.save()

    return redirect('order_placed')

def order_placed(request):
    return render(request, 'orders/order_placed.html')


def view_orders(request):
    orders = Order.objects.filter(placed=True)





    customers = [order.customer for order in orders]
    dates = [order.date for order in orders]
    ids = [order.id for order in orders]
    completeds = [order.completed for order in orders]

    orders_table = list(zip(customers, dates, ids, completeds))

    # row[3] is the boolean "completed"
    orders_table_pending = [row for row in orders_table if not row[3]]
    orders_table_completed = [row for row in orders_table if row[3]]

    variables = {
        'titles': [
            {
                'title': 'Pending orders',
                'condition': False
            },
            {
                'title': 'Completed orders',
                'condition': True
            }
        ],
        'table': orders_table,
        'conditions': [False, True]
    }

    return render(request, 'orders/view_orders.html', variables)

def view_order(request):
    order_id = request.POST.get('order_id', None)
    order = Order.objects.get(id=order_id)

    variables = {
        'customer': order.customer,
        'date': order.date,
        'items': [
            {
                'dish': item.dish,
                'size': item.size,
                'toppings': ', '.join(topping.name for topping in item.toppings.all()),
                'price': item.calculate_price(),
            }
            for item in order.item_set.all()
        ],
        'price': order.price,
        'order_id': order_id,
        'completed': order.completed
    }
    return render(request, 'orders/order.html', variables)



def mark_order_complete(request):
    order_id = request.POST.get('order_id')

    order = Order.objects.get(id=order_id)
    order.completed = True
    order.save()

    request.POST = {'order_id': order_id}
    # sends them back to the same page as if they
    # went back to orders and clicked on the same one
    return view_order(request)

