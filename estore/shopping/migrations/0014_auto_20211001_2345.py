# Generated by Django 3.2.7 on 2021-10-02 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0013_auto_20211001_2309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': 'Addresses'},
        ),
        migrations.AlterField(
            model_name='address',
            name='address2',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
