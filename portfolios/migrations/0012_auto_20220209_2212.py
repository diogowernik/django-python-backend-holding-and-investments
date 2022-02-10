# Generated by Django 3.2 on 2022-02-09 22:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0011_auto_20220209_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolioasset',
            name='shares_amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='portfolio_asset',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='portfolios.portfolioasset'),
        ),
    ]
