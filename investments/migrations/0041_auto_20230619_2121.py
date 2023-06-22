# Generated by Django 3.2 on 2023-06-19 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0040_auto_20230619_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='fii',
            name='is_leveraged',
            field=models.CharField(choices=[('Sim', 'Sim'), ('Não', 'Não'), ('Sem Classificação', 'Sem Classificação')], default='Sem Classificação', max_length=255),
        ),
        migrations.AddField(
            model_name='fii',
            name='leverage_percentage',
            field=models.FloatField(default=0),
        ),
    ]
