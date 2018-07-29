from django.contrib import admin
from .models import *


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_validated']


admin.site.register(Customer, CustomerAdmin)

