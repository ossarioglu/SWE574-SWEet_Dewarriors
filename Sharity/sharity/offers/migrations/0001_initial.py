# Generated by Django 3.2.12 on 2022-04-04 09:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('member', '0002_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('location', models.TextField()),
                ('tags', models.TextField()),
                ('start_date', models.DateTimeField(verbose_name='Start date')),
                ('credit', models.PositiveIntegerField(verbose_name='Credit')),
                ('participant_limit', models.PositiveIntegerField(default=0, verbose_name='Participant limit')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member.owner')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('location', models.TextField()),
                ('tags', models.TextField()),
                ('start_date', models.DateTimeField(verbose_name='Start date')),
                ('credit', models.PositiveIntegerField(verbose_name='Credit')),
                ('participant_limit', models.PositiveIntegerField(default=0, verbose_name='Participant limit')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member.owner')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
