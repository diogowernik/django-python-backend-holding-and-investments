# Generated by Django 3.2 on 2023-07-17 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0024_remove_subscriptionevent_quota_history'),
        ('equity', '0009_auto_20230716_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotahistory',
            name='currency_transaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cashflow.currencytransaction'),
        ),
    ]
