import uuid
import json

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Offer(models.Model):

    class Type(models.IntegerChoices):
        """Type of an Offer"""
        SERVICE = 1, _('Service')
        EVENT = 2, _('Event')

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
    duration = models.PositiveIntegerField(verbose_name=_('Duration'))
    participant_limit = models.PositiveIntegerField(verbose_name=_('Participant limit'), default=0)
    amendment_deadline = models.DateTimeField(verbose_name=_('Amendment deadline'))
    type = models.PositiveSmallIntegerField(
        verbose_name=_('Type'),
        choices=Type.choices,
    )
    photo = models.ImageField(upload_to='static/images/Offers', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('offers.detail', kwargs={'pk': self.pk})

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

    def get_tag_label(self):
        payload = json.loads(str(self.tags).replace("\\'", '"'))
        return payload['label']

    def get_type(self):
        return list(filter(lambda x: x[0] == self.type, self.Type.choices))[0][1]
