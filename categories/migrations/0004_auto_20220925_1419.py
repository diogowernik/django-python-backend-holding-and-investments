# Generated by Django 3.2 on 2022-09-25 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0025_auto_20220925_1419'),
        ('categories', '0003_subcategory'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SetorBrStocks',
        ),
        migrations.DeleteModel(
            name='SetorCrypto',
        ),
    ]
