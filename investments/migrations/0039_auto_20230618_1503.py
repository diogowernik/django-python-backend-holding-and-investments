# Generated by Django 3.2 on 2023-06-18 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0038_rename_liqudity_fii_liquidity'),
    ]

    operations = [
        migrations.AddField(
            model_name='reit',
            name='der',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='reit',
            name='earnings_yield',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='reit',
            name='ffo',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='reit',
            name='p_ffo',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='reit',
            name='roic',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='stocks',
            name='der',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='stocks',
            name='earnings_yield',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='stocks',
            name='ffo',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='stocks',
            name='p_ffo',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='stocks',
            name='roic',
            field=models.FloatField(default=0),
        ),
    ]
