# Generated by Django 3.2 on 2023-07-23 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('equity', '0022_auto_20230723_1359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investevent',
            name='trade_date',
        ),
    ]
