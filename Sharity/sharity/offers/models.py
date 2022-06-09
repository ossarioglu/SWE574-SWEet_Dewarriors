import uuid
import json

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from datetime import timedelta
from actstream import action


class Offer(models.Model):

    def __getitem__(self, x):
        return getattr(self, x)

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
    description = models.TextField(null=True)
    latitude = models.CharField(verbose_name=_('Latitude'), max_length=500, null=True)
    longitude = models.CharField(verbose_name=_('Longitude'), max_length=500, null=True)
    location = models.TextField()
    tags = models.TextField()
    claims = models.TextField(null=True, default='[]')
    owner = models.ForeignKey(
        'member.Owner',
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField(verbose_name=_('Start date'))
    duration = models.PositiveIntegerField(verbose_name=_('Duration'))
    end_date = models.DateTimeField(verbose_name=_('End date'), null=True)
    participant_limit = models.PositiveIntegerField(verbose_name=_('Participant limit'), default=0)
    amendment_deadline = models.DateTimeField(verbose_name=_('Amendment deadline'))
    type = models.PositiveSmallIntegerField(
        verbose_name=_('Type'),
        choices=Type.choices,
    )
    photo = models.ImageField(upload_to='static/images/Offers', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Override end_date attribute"""
        print(self.uuid)
        action.send(self.owner, verb='created an offer', action_object=self)
        self.end_date = self.start_date + timedelta(hours=self.duration)
        super().save(*args, **kwargs)

    @property
    def owner_badges(self):
        return [getattr(self.owner, badge) for badge in ['Nbadge', 'CBbadge', 'GSPbadge', 'MEObadge'] if hasattr(self.owner, badge)]

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

    def get_tag_labels(self):
        payload = json.loads(str(self.tags).replace("\\'", '"'))

        if isinstance(payload, list):
            return [tag['label'] for tag in payload]
        else:
            return [payload['label']]

    def get_type(self):
        return list(filter(lambda x: x[0] == self.type, self.Type.choices))[0][1]
