# Generated by Django 3.2 on 2024-07-01 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equity', '0035_auto_20240701_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoliototalhistory',
            name='event_type',
            field=models.CharField(default='none', max_length=20),
        ),
    ]
