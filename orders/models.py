from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Topping(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.name} (${self.price})"


class MenuSection(models.Model):
    title = models.CharField(max_length=30)

    global_available_toppings = models.ManyToManyField(Topping, blank=True)

    topping_price_is_included = models.BooleanField("Prices for toppings are included in the price of the dish")

    dishes_included = models.ManyToManyField('Dish', blank=True)

    def __str__(self):
        return self.title


class Dish(models.Model):
    name = models.CharField(max_length=30)

    min_global_toppings = models.PositiveSmallIntegerField(default=0)
    max_global_toppings = models.PositiveSmallIntegerField(default=0)

    min_local_toppings = models.PositiveSmallIntegerField(default=0)
    max_local_toppings = models.PositiveSmallIntegerField(default=0)

    price = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    price_small = models.DecimalField("Small size price", max_digits=4, decimal_places=2, null=True, blank=True)
    price_large = models.DecimalField("Large size price", max_digits=4, decimal_places=2, null=True, blank=True)

    menu_section = models.ForeignKey(MenuSection, on_delete=models.CASCADE)

    local_available_toppings = models.ManyToManyField(Topping, blank=True)

    def get_global_available_toppings(self):
        return self.menu_section.global_available_toppings

    def __str__(self):
        return f"{self.menu_section}: {self.name}"

class Item(models.Model):

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)

    size_choices = [] # initialized in the create method
    size = models.CharField(max_length=10, choices=size_choices)

    toppings = models.ManyToManyField(Topping, blank=True)

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
            print(sum(float(topping.price) for topping in self.toppings.all()))
            return price + sum(float(topping.price) for topping in self.toppings.all())

@receiver(post_save, sender=Dish)
def my_handler(sender, **kwargs):
    for menu_section in MenuSection.objects.all():
        menu_section.dishes_included.clear()
    for dish in Dish.objects.all():
        dish.menu_section.dishes_included.add(dish)
