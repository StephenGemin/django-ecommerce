# Generated by Django 3.2.7 on 2021-09-30 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0009_auto_20210930_0203'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default=123, max_length=30),
            preserve_default=False,
        ),
    ]
