# Generated by Django 3.2.7 on 2021-09-14 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0019_alter_billingaddress_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='postal_code',
            field=models.CharField(max_length=6),
        ),
    ]