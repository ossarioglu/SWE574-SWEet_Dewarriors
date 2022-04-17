# Generated by Django 3.2.13 on 2022-04-17 08:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('apply', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('assignID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('serviceType', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Confirmed by provider', 'Confirmed by provider'), ('Confirmed by receiver', 'Confirmed by receiver'), ('Closed', 'Closed')], default='Open', max_length=100)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('approverID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approverForAssignementID', to=settings.AUTH_USER_MODEL)),
                ('requestID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apply.application')),
                ('requesterID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requesterForAssignementID', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
