# Generated by Django 3.2 on 2023-06-25 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0043_asset_ideal_percentage'),
        ('brokers', '0004_alter_broker_main_currency'),
        ('portfolios', '0061_auto_20230620_1427'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='portfolioinvestment',
            unique_together={('portfolio', 'asset', 'broker')},
        ),
        migrations.RemoveField(
            model_name='portfolioinvestment',
            name='desired_percentage',
        ),
        migrations.RemoveField(
            model_name='portfolioinvestment',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='portfolioinvestment',
            name='total_cost_brl',
        ),
        migrations.RemoveField(
            model_name='portfolioinvestment',
            name='total_cost_usd',
        ),
        migrations.RemoveField(
            model_name='portfolioinvestment',
            name='total_today_brl',
        ),
        migrations.RemoveField(
            model_name='portfolioinvestment',
            name='total_today_usd',
        ),
    ]
