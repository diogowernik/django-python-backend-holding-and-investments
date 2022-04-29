# Generated by Django 3.2 on 2022-04-26 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dividends', '0001_initial'),
        ('portfolios', '0022_auto_20220426_1552'),
        ('categories', '0001_initial'),
        ('investments', '0015_privateasset'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ETF',
            new_name='Stocks',
        ),
        migrations.RemoveField(
            model_name='dividend',
            name='asset',
        ),
        migrations.AlterModelOptions(
            name='crypto',
            options={'verbose_name_plural': 'Cripto Currencies'},
        ),
        migrations.AlterModelOptions(
            name='fii',
            options={'verbose_name_plural': '  Brazilian Reits'},
        ),
        migrations.AlterModelOptions(
            name='fixedincome',
            options={'verbose_name_plural': '    Fixed Incomes'},
        ),
        migrations.AlterModelOptions(
            name='privateasset',
            options={'verbose_name_plural': '  Private Assets'},
        ),
        migrations.AlterModelOptions(
            name='stocks',
            options={'verbose_name_plural': '   Stocks'},
        ),
        migrations.AlterField(
            model_name='asset',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='categories.category'),
        ),
        migrations.AlterField(
            model_name='crypto',
            name='setor_crypto',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='setor_cryptos', to='categories.setorcrypto'),
        ),
        migrations.AlterField(
            model_name='fii',
            name='setor_fii',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='setor_fiis', to='categories.setorfii'),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Dividend',
        ),
        migrations.DeleteModel(
            name='SetorCrypto',
        ),
        migrations.DeleteModel(
            name='SetorFii',
        ),
    ]