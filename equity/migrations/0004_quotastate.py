# Generated by Django 3.2 on 2023-07-16 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0068_auto_20230705_2026'),
        ('equity', '0003_auto_20230716_1551'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuotaState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_quotas', models.FloatField()),
                ('quota_price_brl', models.FloatField()),
                ('quota_price_usd', models.FloatField()),
                ('portfolio', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='portfolios.portfolio')),
            ],
        ),
    ]
