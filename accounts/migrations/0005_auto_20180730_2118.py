# Generated by Django 2.0.7 on 2018-07-30 21:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0026_remove_menusection_dishes_included'),
        ('accounts', '0004_auto_20180730_1937'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=10)),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Dish')),
            ],
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='order',
            name='items',
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Customer'),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AddField(
            model_name='item',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Order'),
        ),
        migrations.AddField(
            model_name='item',
            name='toppings',
            field=models.ManyToManyField(blank=True, to='orders.Topping'),
        ),
    ]
