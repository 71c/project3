from django.db import models
from django.contrib.auth.models import User

from orders.models import *


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=255, default=1)
    email_validated = models.BooleanField(default=False)
    cart = models.OneToOneField('Order', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return str(self.user)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    date = models.DateTimeField(null=True)


class Item(models.Model):

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)

    size_choices = [] # initialized in the create method
    size = models.CharField(max_length=10, choices=size_choices)

    toppings = models.ManyToManyField(Topping, blank=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.dish}' + (f' ({self.size})' if self.size != 'Regular' else '')

    @classmethod
    def create(cls, dish):
        size_choices = []
        if dish.price != None:
            size_choices += [('regular', 'Regular')]
        if dish.price_small != None:
            size_choices += [('small', 'Small')]
        if dish.price_large != None:
            size_choices += [('large', 'Large')]
        item = cls(
            dish=dish,
        )
        item.size_choices=size_choices
        return item

    def get_size_dict(self):
        sizes_and_prices = dict()
        for size_name, size in self.size_choices:
            if size == 'Regular':
                sizes_and_prices['Regular'] = self.dish.price
            elif size == 'Small':
                sizes_and_prices['Small'] = self.dish.price_small
            elif size == 'Large':
                sizes_and_prices['Large'] = self.dish.price_large
        return sizes_and_prices

    def get_global_available_toppings(self):
        return self.dish.get_global_available_toppings().all()
    def get_local_available_toppings(self):
        return self.dish.local_available_toppings.all()

    def calculate_price(self):
        price = {"Regular": self.dish.price, "Small": self.dish.price_small, "Large": self.dish.price_large, "": self.dish.price}[self.size]
        if self.dish.menu_section.topping_price_is_included:
            return price
        else:
            return price + sum(float(topping.price) for topping in self.toppings.all())
