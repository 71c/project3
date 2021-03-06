# Generated by Django 2.0.7 on 2018-07-26 17:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20180726_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='max_toppings',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dish',
            name='min_toppings',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dish',
            name='toppings',
            field=models.ManyToManyField(blank=True, null=True, to='orders.Topping'),
        ),
        migrations.AlterField(
            model_name='topping',
            name='menu_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.MenuSection'),
        ),
    ]
