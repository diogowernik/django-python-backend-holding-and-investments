# Generated by Django 3.2 on 2023-07-23 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0068_auto_20230705_2026'),
        ('equity', '0026_alter_quotahistory_event_type'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AssetValuationEvent',
            new_name='ValuationEvent',
        ),
    ]
