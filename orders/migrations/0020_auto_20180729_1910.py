# Generated by Django 2.0.7 on 2018-07-29 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0019_auto_20180729_1908'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menusection',
            name='toppings_included',
        ),
        migrations.AddField(
            model_name='dish',
            name='max_local_toppings',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dish',
            name='min_local_toppings',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
