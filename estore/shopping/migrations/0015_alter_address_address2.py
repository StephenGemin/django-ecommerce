# Generated by Django 3.2.7 on 2021-10-02 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0014_auto_20211001_2345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
