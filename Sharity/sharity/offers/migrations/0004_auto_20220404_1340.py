# Generated by Django 3.2.12 on 2022-04-04 10:40

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_owner'),
        ('offers', '0003_auto_20220404_1304'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('location', models.TextField()),
                ('tags', models.TextField()),
                ('start_date', models.DateTimeField(verbose_name='Start date')),
                ('duration', models.PositiveIntegerField(verbose_name='Duration')),
                ('participant_limit', models.PositiveIntegerField(default=0, verbose_name='Participant limit')),
                ('amendment_deadline', models.DateTimeField(verbose_name='Amendment deadline')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Service'), (2, 'Event')], verbose_name='Type')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member.owner')),
            ],
        ),
        migrations.RemoveField(
            model_name='service',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
    ]
