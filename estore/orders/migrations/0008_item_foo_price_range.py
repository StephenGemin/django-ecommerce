# Generated by Django 3.2.7 on 2021-09-07 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20210907_1621'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='item',
            constraint=models.CheckConstraint(check=models.Q(('price__gte', 0.0)), name='foo_price_range'),
        ),
    ]
