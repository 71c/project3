from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.utils.timezone import now

from django.contrib import messages

from accounts.models import *

# renders the menu
def menu(request):
    menu = [
        {
            'title': str(menu_section),
            'dishes': menu_section.dish_set.all()
        } for menu_section in MenuSection.objects.all()
    ]
    return render(request, 'orders/menu.html', {'menu': menu})

# renders a given dish
def render_dish(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        dish = Dish.objects.get(id=dish_id)

        item = Item.create(dish)
        sizes_and_prices = item.get_size_dict()
        there_is_one_size = len(sizes_and_prices) == 1

        # attributes of the dish!
        dish_info = {
            'dish_name': item.dish.name,
            'sizes_and_prices': sizes_and_prices,
            'sizes_and_prices_items': sizes_and_prices.items(),
            'there_is_one_size': there_is_one_size,
            'topping_price_is_included': item.dish.menu_section.topping_price_is_included,
            'dish_id': dish.id
        }

        min_global_toppings = item.dish.min_global_toppings
        max_global_toppings = item.dish.max_global_toppings
        min_local_toppings = item.dish.min_local_toppings
        max_local_toppings = item.dish.max_local_toppings

        global_available_toppings = item.get_global_available_toppings()
        local_available_toppings = item.get_local_available_toppings()

        # A table of minimum and maximum toppings, the toppings, and name,
        # that the template can traverse over so it doesn't need to repeat itself
        min_max_and_lists = [
            (min_global_toppings, max_global_toppings, global_available_toppings, 'global'),
            (min_local_toppings, max_local_toppings, local_available_toppings, 'local')
        ]

        # If there is a single price for the dish, we give the template that because otherwise it can't get it.
        single_price = list(dish_info['sizes_and_prices_items'])[0][1]

        dish_info['min_max_and_lists'] = min_max_and_lists
        dish_info['single_price'] = single_price

        # If the user didn't fill out the form right, the page will be re-loaded with those errors.
        # I looked the django messages module and AJAX but I couldn't get them to work.
        errors = request.POST.get('errors')
        if errors != None:
            dish_info['errors'] = errors

        return render(request, 'orders/dish.html', dish_info)

# adds an item to the customer's cart
def add_to_cart(request):
    # Form "errors" are added to this list
    errors = []

    post = request.POST

    if not request.user.is_authenticated:
        errors += ["You're not logged in!"]

    size = post.get('size')
    size_is_selected = size != None
    if not size_is_selected:
        errors += ['You need to pick a size']

    dish_id = post.get('dish_id')
    dish = Dish.objects.get(id=dish_id)

    # create an item from the dish.
    # I meade a create method in Item which does this.
    item = Item.create(dish)
    item.size = size

    # all the toppings (the ids of them)
    topping_ids = post.getlist('toppings')
    # if there are any toppings
    if topping_ids != None:
        topping_ids = [id_and_type.split(',') for id_and_type in topping_ids]
        global_topping_ids = [topping_id for topping_id, topping_type in topping_ids if topping_type == 'global']
        local_topping_ids = [topping_id for topping_id, topping_type in topping_ids if topping_type == 'local']

        global_toppings_in_range = dish.min_global_toppings <= len(global_topping_ids) <= dish.max_global_toppings
        local_toppings_in_range = dish.min_local_toppings <= len(local_topping_ids) <= dish.max_local_toppings

        # make the right error messages
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

        # if there are any errors
        if len(errors) > 0:
            dish_data = {
              'dish_id': dish_id,
              'errors': errors
            }
            request.POST = dish_data
            # reload the page, along with the new error messages
            return render_dish(request)

        item.save()

        # add the toppings to the item
        if global_topping_ids != None:
            for topping_id in global_topping_ids:
                item.toppings.add(Topping.objects.get(id=topping_id))
        if local_topping_ids != None:
            for topping_id in local_topping_ids:
                item.toppings.add(Topping.objects.get(id=topping_id))

    current_customer = request.user.customer

    # if the customer's cart is empty -- their foreign key called cart that points to an Order is null -- create a new one
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

# send a message that an item was added to the customer's cart
def added_to_cart(request):
    return render(request, 'orders/added_to_cart.html')

# displays the customer's cart.
def cart(request):
    current_customer = request.user.customer

    cart = current_customer.cart

    # Make the cart an empty list if it is None; otherwise, its Items
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
                'toppings': item.toppings.all(),
                'price': item.calculate_price()
            }
            for item in cart_items
        ]
    return render(request, 'orders/cart.html', variables)

# Places an order, when the customer presses a button
def place_order(request):
    customer = request.user.customer

    # reference the Order to the Customer
    customer.cart.customer = customer
    # configure the Order
    customer.cart.date = now()
    customer.cart.placed = True
    customer.cart.update_price()

    customer.cart.save()

    # "clear cart" -- get rid of the customer's reference to the order
    customer.cart = None
    customer.save()

    return redirect('order_placed')

# notifies the customer that their order has been placed
def order_placed(request):
    return render(request, 'orders/order_placed.html')

# shows the orders
def view_orders(request):
    # only displays orders if user is signed in
    if request.user.is_authenticated:
        orders = Order.objects.filter(placed=True)
        if not request.user.is_staff:
            orders = orders.filter(customer=request.user.customer)


        customers = [order.customer for order in orders]
        dates = [order.date for order in orders]
        ids = [order.id for order in orders]
        completeds = [order.completed for order in orders]

        # table of orders, sorted by time, descending
        orders_table = sorted(zip(customers, dates, ids, completeds), key = lambda x: x[1])[::-1]

        variables = {
            'titles': [
                {
                    'title': 'Pending orders',
                    'condition': False,

                    # whether there are any orders at all in this section
                    # Allows the template to not render the table headers, which looks funhny
                    'any': any(not completed for completed in completeds)
                },
                {
                    'title': 'Completed orders',
                    'condition': True,
                    'any': any(completeds)
                }
            ],
            'table': orders_table,
        }
        return render(request, 'orders/view_orders.html', variables)
    return render(request, 'orders/view_orders.html')

# displays an order, as two tables
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
                'toppings': item.toppings.all(),
                'price': item.calculate_price(),
            }
            for item in order.item_set.all()
        ],
        'price': order.price,
        'order_id': order_id,
        'completed': order.completed,
        'completed_date': order.completed_date
    }
    return render(request, 'orders/order.html', variables)

# marks an order as complete when an admin clicks the button on an order page, and reloads the page
def mark_order_complete(request):
    order_id = request.POST.get('order_id')

    order = Order.objects.get(id=order_id)
    order.completed = True
    order.completed_date = now()
    order.save()

    request.POST = {'order_id': order_id}
    # sends them back to the same page as if they
    # went back to orders and clicked on the same one
    return view_order(request)

