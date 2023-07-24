# Generated by Django 3.2 on 2023-07-23 13:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0028_auto_20230721_1527'),
        ('brokers', '0011_delete_currency'),
        ('investments', '0048_alter_currencyholding_currency'),
        ('equity', '0021_auto_20230721_1529'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='portfoliohistory',
            options={'verbose_name_plural': 'Histórico de Portfolios'},
        ),
        migrations.CreateModel(
            name='InvestEvent',
            fields=[
                ('currencytransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cashflow.currencytransaction')),
                ('trade_amount', models.FloatField(default=0)),
                ('trade_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('trade_type', models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell')], default='buy', editable=False, max_length=50)),
                ('asset', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='investments.asset')),
                ('to_broker', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='brokers.broker')),
            ],
            bases=('cashflow.currencytransaction',),
        ),
    ]
