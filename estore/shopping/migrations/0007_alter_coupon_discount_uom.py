# Generated by Django 3.2.7 on 2021-09-28 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0006_coupon_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='discount_uom',
            field=models.CharField(choices=[('%', 'percent'), ('$', 'absolute')], max_length=20),
        ),
    ]
