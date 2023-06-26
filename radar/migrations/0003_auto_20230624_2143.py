# Generated by Django 3.2 on 2023-06-24 21:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('radar', '0002_auto_20230622_1628'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='radar',
            name='portfolio_total_value',
        ),
        migrations.RemoveField(
            model_name='radarasset',
            name='delta_ideal_actual_percentage_on_category',
        ),
        migrations.RemoveField(
            model_name='radarasset',
            name='delta_ideal_actual_percentage_on_portfolio',
        ),
        migrations.RemoveField(
            model_name='radarasset',
            name='portfolio_investment_percentage_on_category',
        ),
        migrations.RemoveField(
            model_name='radarasset',
            name='portfolio_investment_percentage_on_portfolio',
        ),
        migrations.RemoveField(
            model_name='radarasset',
            name='portfolio_investment_total_value',
        ),
        migrations.RemoveField(
            model_name='radarcategory',
            name='category_percentage_on_portfolio',
        ),
        migrations.RemoveField(
            model_name='radarcategory',
            name='category_total_value',
        ),
        migrations.RemoveField(
            model_name='radarcategory',
            name='delta_ideal_actual_percentage',
        ),
        migrations.AlterField(
            model_name='radarasset',
            name='ideal_asset_percentage_on_category',
            field=models.FloatField(default=0.1),
        ),
        migrations.AlterField(
            model_name='radarasset',
            name='radar',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='radar.radar'),
        ),
        migrations.AlterField(
            model_name='radarasset',
            name='radar_category',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='radar.radarcategory'),
        ),
    ]
