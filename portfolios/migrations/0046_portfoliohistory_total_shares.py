# Generated by Django 3.2 on 2022-10-25 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0045_auto_20221025_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoliohistory',
            name='total_shares',
            field=models.FloatField(default=0),
        ),
    ]
