# Generated by Django 3.2 on 2024-02-05 17:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kids', '0004_kidsearns_kidsexpenses'),
    ]

    operations = [
        migrations.AddField(
            model_name='kidsearns',
            name='belongs_to',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='kids.kidprofile', verbose_name='Pertence a'),
        ),
        migrations.AddField(
            model_name='kidsexpenses',
            name='belongs_to',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='kids.kidprofile', verbose_name='Pertence a'),
        ),
    ]
