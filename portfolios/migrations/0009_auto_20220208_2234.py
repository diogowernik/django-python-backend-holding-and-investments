# Generated by Django 3.2 on 2022-02-08 22:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0012_fixedincome_default_currency'),
        ('portfolios', '0008_auto_20220208_1608'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brokerasset',
            options={'verbose_name_plural': '  Assets per Broker'},
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='broker_asset',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='broker_average_price',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='portfolio_asset',
        ),
        migrations.AddField(
            model_name='transaction',
            name='asset',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='investments.asset'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='portfolio',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='portfolios.portfolio'),
        ),
    ]