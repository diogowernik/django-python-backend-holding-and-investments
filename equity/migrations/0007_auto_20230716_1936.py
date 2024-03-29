# Generated by Django 3.2 on 2023-07-16 19:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equity', '0006_subscriptionevent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quotastate',
            name='portfolio',
        ),
        migrations.RemoveField(
            model_name='subscriptionevent',
            name='quotaevent_ptr',
        ),
        migrations.RemoveField(
            model_name='quotahistory',
            name='total_quotas',
        ),
        migrations.AddField(
            model_name='quotahistory',
            name='percentage_change',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='quotahistory',
            name='quota_amount',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='quotahistory',
            name='total_today_brl',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='quotahistory',
            name='total_today_usd',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='quotahistory',
            name='transaction_amount_brl',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='quotahistory',
            name='transaction_amount_usd',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='quotahistory',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='quotahistory',
            name='event_type',
            field=models.CharField(choices=[('Deposit', 'Deposit'), ('Withdraw', 'Withdraw'), ('Valuation', 'Valuation')], default='Deposit', max_length=20),
        ),
        migrations.AlterField(
            model_name='quotahistory',
            name='quota_price_brl',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='quotahistory',
            name='quota_price_usd',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.DeleteModel(
            name='QuotaEvent',
        ),
        migrations.DeleteModel(
            name='QuotaState',
        ),
        migrations.DeleteModel(
            name='SubscriptionEvent',
        ),
    ]
