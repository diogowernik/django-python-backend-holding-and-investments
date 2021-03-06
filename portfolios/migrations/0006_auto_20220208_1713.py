# Generated by Django 3.2 on 2022-02-08 17:13

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0005_auto_20220203_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='new_average_price',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=18),
        ),
        migrations.CreateModel(
            name='BrokerAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shares_amount', models.DecimalField(decimal_places=2, max_digits=18)),
                ('share_average_price_brl', models.DecimalField(decimal_places=2, max_digits=18)),
                ('total_cost_brl', models.DecimalField(decimal_places=2, editable=False, max_digits=18)),
                ('total_today_brl', models.DecimalField(decimal_places=2, editable=False, max_digits=18)),
                ('broker', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='portfolios.broker')),
                ('portfolio_asset', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='portfolios.portfolioasset')),
            ],
        ),
    ]
