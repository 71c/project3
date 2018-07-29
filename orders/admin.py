from django.contrib import admin
from .models import *

class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'topping_price_is_included']
    ordering = ['title']

class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'menu_section', 'price', 'price_small', 'price_large']
    ordering = ['menu_section']

admin.site.register(MenuSection, MenuSectionAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Topping)
admin.site.register(Item)