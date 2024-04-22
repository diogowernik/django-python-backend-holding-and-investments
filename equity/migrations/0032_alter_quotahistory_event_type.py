# Generated by Django 3.2 on 2024-01-28 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equity', '0031_auto_20230901_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotahistory',
            name='event_type',
            field=models.CharField(choices=[('deposit', 'deposit'), ('withdraw', 'withdraw'), ('valuation', 'valuation'), ('dividend receive', 'dividend receive'), ('dividend payment', 'dividend payment'), ('invest br', 'invest br'), ('divest br', 'divest br'), ('invest us', 'invest us'), ('divest us', 'divest us'), ('tax payment', 'tax payment')], default='deposit', max_length=20),
        ),
    ]