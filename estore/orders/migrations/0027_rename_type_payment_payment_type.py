# Generated by Django 3.2.7 on 2021-09-16 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0026_auto_20210916_0205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='type',
            new_name='payment_type',
        ),
    ]
