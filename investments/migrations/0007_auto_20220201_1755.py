# Generated by Django 3.2 on 2022-02-01 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0006_asset_broker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='broker',
        ),
        migrations.DeleteModel(
            name='Broker',
        ),
    ]
