# Generated by Django 3.2 on 2023-06-29 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('brokers', '0007_broker_main_currency'),
        ('investments', '0044_auto_20230629_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='currencyholding',
            name='currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='brokers.currency'),
        ),
    ]