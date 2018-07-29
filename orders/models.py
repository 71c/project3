from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Topping(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    menu_sections = models.ManyToManyField('MenuSection', blank=True, related_name='menu_sections')

    def __str__(self):
        return f"{self.name} (${self.price})"


class MenuSection(models.Model):
    title = models.CharField(max_length=30)

    available_toppings = models.ManyToManyField(Topping, blank=True, related_name='available_toppings')
    toppings_included = models.ManyToManyField(Topping, blank=True, related_name='toppings_included')

    topping_price_is_included = models.BooleanField("Prices for toppings are included in the price of the dish")

    dishes_included = models.ManyToManyField('Dish', blank=True)

    def __str__(self):
        return self.title


class Dish(models.Model):

    name = models.CharField(max_length=30)

    min_toppings = models.PositiveSmallIntegerField(default=0)
    max_toppings = models.PositiveSmallIntegerField(default=0)

    price = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    price_small = models.DecimalField("Small size price", max_digits=4, decimal_places=2, null=True, blank=True)
    price_large = models.DecimalField("Large size price", max_digits=4, decimal_places=2, null=True, blank=True)

    menu_section = models.ForeignKey(MenuSection, on_delete=models.CASCADE)

    def calculate_price(self, size, toppings):
        price = {"regular": self.price, "small": self.price_small, "large": self.price_large}[size]
        if self.topping_price_is_included:
            return price
        else:
            return price + sum(topping.price for topping in toppings)

    def get_available_toppings(self):
        return self.menu_section.available_toppings

    def __str__(self):
        return f"{self.menu_section}: {self.name}"

class Item(models.Model):
    SIZE_CHOICES = (
        ('small', 'Small'),
        ('large', 'Large'),
        ('regular', 'Regular')
    )

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    toppings = models.ManyToManyField(Topping, blank=True)

    def calculate_price(self):
        price = {"regular": self.dish.price, "small": self.dish.price_small, "large": self.dish.price_large}[self.size]
        if self.dish.topping_price_is_included:
            return price
        else:
            return price + sum(topping.price for topping in self.toppings)


@receiver(post_save, sender=Dish)
def my_handler(sender, **kwargs):
    for menu_section in MenuSection.objects.all():
        menu_section.dishes_included.clear()
    for dish in Dish.objects.all():
        dish.menu_section.dishes_included.add(dish)
