# Generated by Django 3.2.7 on 2021-09-08 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_alter_item_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='price_discount',
            field=models.FloatField(blank=True, null=True),
        ),
    ]