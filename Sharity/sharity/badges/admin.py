from django.contrib import admin
from .models import (
    # UserBadge,
    CommunityBuilderBadge, 
    MasterEventOrganizerBadge,
    GreatServiceProviderBadge,
    NewcomerBadge
)

# Register your models here.
admin.site.register([CommunityBuilderBadge, MasterEventOrganizerBadge, GreatServiceProviderBadge, NewcomerBadge])