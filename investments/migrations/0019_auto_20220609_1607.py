# Generated by Django 3.2 on 2022-06-09 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0018_auto_20220609_1607'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fixedincome',
            name='credit',
        ),
        migrations.AlterField(
            model_name='fixedincome',
            name='credit_type',
            field=models.CharField(choices=[('Bancario', 'Bancario'), ('Soberano', 'Soberano'), ('Privado', 'Privado')], default='Bancario', max_length=255),
        ),
    ]
