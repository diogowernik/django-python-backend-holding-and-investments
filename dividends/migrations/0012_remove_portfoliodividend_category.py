# Generated by Django 3.2 on 2023-07-09 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dividends', '0011_auto_20230707_1156'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfoliodividend',
            name='category',
        ),
    ]
