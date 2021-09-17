# Generated by Django 3.2.7 on 2021-09-17 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0027_rename_type_payment_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(choices=[('Stripe', 'Stripe'), ('PayPal', 'PayPal'), ('BitCoin', 'BitCoin')], max_length=50),
        ),
    ]