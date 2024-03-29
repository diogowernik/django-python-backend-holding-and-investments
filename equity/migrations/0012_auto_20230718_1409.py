# Generated by Django 3.2 on 2023-07-18 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0068_auto_20230705_2026'),
        ('cashflow', '0025_delete_subscriptionevent'),
        ('equity', '0011_subscriptionevent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quotahistory',
            old_name='total_today_brl',
            new_name='total_brl',
        ),
        migrations.RenameField(
            model_name='quotahistory',
            old_name='total_today_usd',
            new_name='total_usd',
        ),
        migrations.RenameField(
            model_name='quotahistory',
            old_name='transaction_amount_brl',
            new_name='value_brl',
        ),
        migrations.RenameField(
            model_name='quotahistory',
            old_name='transaction_amount_usd',
            new_name='value_usd',
        ),
        migrations.CreateModel(
            name='PortfolioHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total_brl', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total_usd', models.DecimalField(decimal_places=2, max_digits=20)),
                ('currency_transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cashflow.currencytransaction')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolios.portfolio')),
            ],
        ),
    ]
