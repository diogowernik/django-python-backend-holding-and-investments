# Generated by Django 3.2 on 2022-06-25 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0021_auto_20220625_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='brstocks',
            name='ranking_all',
            field=models.FloatField(default=0),
        ),
    ]
