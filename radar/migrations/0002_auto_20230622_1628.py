# Generated by Django 3.2 on 2023-06-22 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('radar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='radarasset',
            name='radar_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='radar.radarcategory'),
        ),
        migrations.AlterField(
            model_name='radarasset',
            name='ideal_asset_percentage_on_portfolio',
            field=models.FloatField(default=0.0, editable=False),
        ),
    ]
