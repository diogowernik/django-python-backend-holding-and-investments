# Generated by Django 3.2 on 2023-07-18 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equity', '0012_auto_20230718_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoliohistory',
            name='total_brl',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='portfoliohistory',
            name='total_usd',
            field=models.FloatField(default=0),
        ),
    ]
