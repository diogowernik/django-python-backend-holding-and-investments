# Generated by Django 3.2 on 2023-06-26 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('radar', '0004_auto_20230626_1152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='radarasset',
            name='radar_category',
            field=models.ForeignKey(default=2, editable=False, on_delete=django.db.models.deletion.CASCADE, to='radar.radarcategory'),
            preserve_default=False,
        ),
    ]
