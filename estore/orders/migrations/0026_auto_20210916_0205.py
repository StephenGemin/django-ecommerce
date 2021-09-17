# Generated by Django 3.2.7 on 2021-09-16 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_remove_payment_payment_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='stripe_charge_id',
            new_name='payment_id',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='stripe_charge_obj',
            new_name='payment_obj',
        ),
        migrations.AddField(
            model_name='payment',
            name='type',
            field=models.CharField(choices=[('Stripe', 'Stripe'), ('PayPal', 'PayPal'), ('Credit', 'Credit'), ('BitCoin', 'BitCoin')], default='Stripe', max_length=50),
            preserve_default=False,
        ),
    ]