from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# represents a topping.
class Topping(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.name} (${self.price})"

# reperesents a section of the menu.
class MenuSection(models.Model):
    title = models.CharField(max_length=30)

    # all Dishes contained in the MenuSection can have these toppings on them.
    global_available_toppings = models.ManyToManyField(Topping, blank=True)

    # whether toppings are free for all children Dishes
    topping_price_is_included = models.BooleanField("Prices for toppings are included in the price of the dish")

    def __str__(self):
        return self.title


class Dish(models.Model):
    name = models.CharField(max_length=30)

    # min and max toppings inherited from the dishes menu section that can be on the dish
    min_global_toppings = models.PositiveSmallIntegerField(default=0)
    max_global_toppings = models.PositiveSmallIntegerField(default=0)

    # min and max toppings made available for this specific dish that can be on the dish
    min_local_toppings = models.PositiveSmallIntegerField(default=0)
    max_local_toppings = models.PositiveSmallIntegerField(default=0)

    # price for dish, if there is no options for small and large
    price = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    price_small = models.DecimalField("Small size price", max_digits=4, decimal_places=2, null=True, blank=True)
    price_large = models.DecimalField("Large size price", max_digits=4, decimal_places=2, null=True, blank=True)

    menu_section = models.ForeignKey(MenuSection, on_delete=models.CASCADE)

    # toppings you can pick for this dish, specific for this dish.
    # Global and local toppings were only introduced to accomodate the special case of the steak sub.
    local_available_toppings = models.ManyToManyField(Topping, blank=True)

    def get_global_available_toppings(self):
        return self.menu_section.global_available_toppings

    def __str__(self):
        return f"{self.menu_section}: {self.name}"


