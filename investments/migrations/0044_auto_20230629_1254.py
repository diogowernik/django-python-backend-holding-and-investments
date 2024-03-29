# Generated by Django 3.2 on 2023-06-29 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radar', '0006_alter_radarasset_radar_category'),
        ('portfolios', '0066_remove_portfolioinvestment_is_radar'),
        ('categories', '0008_delete_tag'),
        ('dividends', '0005_auto_20221004_2140'),
        ('investments', '0043_asset_ideal_percentage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Currency',
            new_name='CurrencyHolding',
        ),
        migrations.RemoveField(
            model_name='fii',
            name='last_dividend',
        ),
        migrations.RemoveField(
            model_name='fii',
            name='last_yield',
        ),
        migrations.RemoveField(
            model_name='fii',
            name='six_m_yield',
        ),
    ]
