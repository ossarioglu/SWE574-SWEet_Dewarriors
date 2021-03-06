# Generated by Django 3.2.13 on 2022-04-18 17:12

from django.db import migrations, models
from django.core.management import call_command


class Migration(migrations.Migration):
    dependencies = [
        ('apply', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(
                choices=[('Inprocess', 'Inprocess'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')],
                default='Open', max_length=100),
        ),
    ]
