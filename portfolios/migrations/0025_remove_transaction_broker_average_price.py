# Generated by Django 3.2 on 2022-05-10 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0024_auto_20220508_1334'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='broker_average_price',
        ),
    ]
