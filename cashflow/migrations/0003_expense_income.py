# Generated by Django 3.2 on 2023-07-06 00:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0002_auto_20230706_0035'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('currencytransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cashflow.currencytransaction')),
                ('transaction_category', models.CharField(choices=[('Cartão de Crédito', 'Cartão de Crédito'), ('Casa', 'Casa'), ('Manutenção de Ativos', 'Manutenção de Ativos'), ('Imposto', 'Imposto')], default='Cartão de Crédito', max_length=255)),
            ],
            options={
                'verbose_name': 'Despesa',
                'verbose_name_plural': 'Despesas',
            },
            bases=('cashflow.currencytransaction',),
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('currencytransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cashflow.currencytransaction')),
                ('transaction_category', models.CharField(choices=[('Renda Ativa', 'Renda Ativa'), ('Renda Extra', 'Renda Extra'), ('Renda Passiva', 'Renda Passiva'), ('Outros', 'Outros')], default='Renda Ativa', max_length=255)),
            ],
            options={
                'verbose_name': 'Receita',
                'verbose_name_plural': 'Receitas',
            },
            bases=('cashflow.currencytransaction',),
        ),
    ]
