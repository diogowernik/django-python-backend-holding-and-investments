# Generated by Django 3.2 on 2023-07-13 18:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0001_initial'),
        ('dividends', '0014_portfoliodividend_transaction_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoliodividend',
            name='transaction_history',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trade.transactionshistory'),
        ),
    ]