# Generated by Django 3.2.7 on 2021-09-30 08:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0011_refund'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='refund_complete',
            new_name='refund_granted',
        ),
    ]
