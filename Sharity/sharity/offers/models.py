import uuid
import json

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Offer(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    title = models.CharField(verbose_name=_('Title'), max_length=500)
    location = models.TextField()
    tags = models.TextField()
    owner = models.ForeignKey(
        'member.Owner',
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField(verbose_name=_('Start date'))
    credit = models.PositiveIntegerField(verbose_name=_('Credit'))
    participant_limit = models.PositiveIntegerField(verbose_name=_('Participant limit'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('services.detail', kwargs={'pk': self.pk})

    def get_latitude(self):
        payload = json.loads(str(self.location).replace("\\'", '"'))
        return payload['geometry']['location']['lat']

    def get_longitude(self):
        payload = json.loads(str(self.location).replace("\\'", '"'))
        return payload['geometry']['location']['lng']

    def get_formatted_address(self):
        payload = json.loads(str(self.location).replace("\\'", '"'))
        return payload['formatted_address']

    def get_location_type_icon(self):
        payload = json.loads(str(self.location).replace("\\'", '"'))
        return payload['icon']


class Service(Offer):
    pass


class Event(Offer):
    pass
