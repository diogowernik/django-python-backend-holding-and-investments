# Generated by Django 3.2 on 2024-01-28 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('brokers', '0011_delete_currency'),
        ('portfolios', '0068_auto_20230705_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoliodividend',
            name='category',
            field=models.CharField(choices=[('Ações Brasileiras', 'Ações Brasileiras'), ('Fundos Imobiliários', 'Fundos Imobiliários'), ('ETF', 'ETF'), ('Stocks', 'Stocks'), ('REITs', 'REITs'), ('Propriedades', 'Propriedades'), ('FII', 'Fundos Imobiliários'), ('FI-Infra', 'Fundos Imobiliários'), ('Ação', 'Ações Brasileiras')], default='Ação', max_length=100),
        ),
        migrations.AlterField(
            model_name='portfolioinvestment',
            name='broker',
            field=models.ForeignKey(default=22, on_delete=django.db.models.deletion.CASCADE, to='brokers.broker'),
        ),
    ]
