# Generated by Django 3.2 on 2023-07-07 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dividends', '0008_remove_portfoliodividend_ticker'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoliodividend',
            name='dividend',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dividends.dividend'),
        ),
    ]
