# Generated by Django 3.2 on 2023-06-19 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0042_auto_20230619_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='ideal_percentage',
            field=models.FloatField(default=0),
        ),
    ]
