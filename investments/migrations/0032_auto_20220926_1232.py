# Generated by Django 3.2 on 2022-09-26 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0031_auto_20220926_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='bottom_52w',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='asset',
            name='dividend_frequency',
            field=models.FloatField(default=4),
        ),
        migrations.AddField(
            model_name='asset',
            name='top_52w',
            field=models.FloatField(default=0),
        ),
    ]
