# Generated by Django 3.2 on 2024-07-01 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0028_auto_20230721_1527'),
        ('equity', '0034_divestbrevent_to_broker'),
    ]

    operations = [
        migrations.CreateModel(
            name='SendMoneyEvent',
            fields=[
                ('internationalcurrencytransfer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cashflow.internationalcurrencytransfer')),
            ],
            options={
                'verbose_name': 'Envio de Dinheiro',
                'verbose_name_plural': '  Envio de Dinheiro',
            },
            bases=('cashflow.internationalcurrencytransfer',),
        ),
        migrations.AlterField(
            model_name='quotahistory',
            name='event_type',
            field=models.CharField(choices=[('deposit', 'deposit'), ('withdraw', 'withdraw'), ('valuation', 'valuation'), ('dividend receive', 'dividend receive'), ('dividend payment', 'dividend payment'), ('invest br', 'invest br'), ('divest br', 'divest br'), ('invest us', 'invest us'), ('divest us', 'divest us'), ('tax payment', 'tax payment'), ('send money', 'send money')], default='deposit', max_length=20),
        ),
    ]
