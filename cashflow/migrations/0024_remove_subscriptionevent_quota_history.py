# Generated by Django 3.2 on 2023-07-17 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0023_subscriptionevent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriptionevent',
            name='quota_history',
        ),
    ]
