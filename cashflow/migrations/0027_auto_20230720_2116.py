# Generated by Django 3.2 on 2023-07-20 21:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0026_alter_currencytransaction_transaction_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='income',
            name='currencytransaction_ptr',
        ),
        migrations.AlterModelOptions(
            name='currencytransfer',
            options={'ordering': ['-transfer_date'], 'verbose_name_plural': 'Transferências entre bancos'},
        ),
        migrations.DeleteModel(
            name='Expense',
        ),
        migrations.DeleteModel(
            name='Income',
        ),
    ]
