# Generated by Django 3.2 on 2023-06-29 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('brokers', '0006_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='broker',
            name='main_currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='brokers.currency'),
        ),
    ]
