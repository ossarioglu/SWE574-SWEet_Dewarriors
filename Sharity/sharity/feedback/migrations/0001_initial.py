# Generated by Django 3.2.13 on 2022-05-16 03:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('offers', '0006_offer_claims'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('feedbackID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('comment', models.TextField()),
                ('rating', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('giverID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbackGiverID', to=settings.AUTH_USER_MODEL)),
                ('serviceID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbackForService', to='offers.offer')),
                ('takerID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbackReceiverID', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
