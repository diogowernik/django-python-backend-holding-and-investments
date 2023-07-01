# Generated by Django 3.2 on 2023-06-29 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brokers', '0005_remove_broker_main_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('price_brl', models.FloatField(default=0)),
                ('price_usd', models.FloatField(default=0)),
            ],
        ),
    ]
