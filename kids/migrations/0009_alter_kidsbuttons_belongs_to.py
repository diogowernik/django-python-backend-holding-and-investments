# Generated by Django 3.2 on 2024-02-16 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kids', '0008_alter_kidsbuttons_belongs_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kidsbuttons',
            name='belongs_to',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_buttons', to='kids.kidprofile'),
        ),
    ]
