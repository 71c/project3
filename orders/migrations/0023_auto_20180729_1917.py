# Generated by Django 2.0.7 on 2018-07-29 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_auto_20180729_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menusection',
            name='global_available_toppings',
            field=models.ManyToManyField(blank=True, to='orders.Topping'),
        ),
    ]
