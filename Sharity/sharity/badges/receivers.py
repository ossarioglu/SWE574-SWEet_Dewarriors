from offers.views import OfferDetailView
from member.models import Profile, Owner
from .models import GreatServiceProviderBadge, MasterEventOrganizerBadge, NewcomerBadge, CommunityBuilderBadge
from django.dispatch import receiver
from .signals import *
from django.utils import timezone


@receiver(timeline)
@receiver(profile_detail, sender=Profile)
@receiver(offer_detail, sender=OfferDetailView)
def award_MEO_badge(sender, owner_pk, **kwargs):
    print('Checking Master Event Organizer badges...')
    for pk in owner_pk:
        # check if the user deserves a badge
        award = MasterEventOrganizerBadge.should_award(pk)
        if award:
            # check if the user has a badge already
            try:
                badge = MasterEventOrganizerBadge.objects.get(owner__pk=pk)
                # check if the badge is active
                badge = badge if badge.is_badge_active else None
            except MasterEventOrganizerBadge.DoesNotExist:
                badge = None

            # if user has an active badge
            if badge:
                # update awarded date
                badge.awarded_date = timezone.now()
                badge.save()
            # if the user does not have an active badge
            else:
                badge = MasterEventOrganizerBadge.objects.create(
                    owner=Owner.objects.get(pk=pk),
                    awarded_date=timezone.now()
                )


@receiver(timeline)
@receiver(profile_detail, sender=Profile)
@receiver(offer_detail, sender=OfferDetailView)
def award_GSP_badge(sender, owner_pk, **kwargs):
    print('Checking Great Service Provider badges...')
    for pk in owner_pk:
        # check if the user deserves a badge
        award = GreatServiceProviderBadge.should_award(pk)
        if award:
            # check if the user has a badge already
            try:
                badge = GreatServiceProviderBadge.objects.get(owner__pk=pk)
                # check if the badge is active
                badge = badge if badge.is_badge_active else None
            except GreatServiceProviderBadge.DoesNotExist:
                badge = None

            # if user has an active badge
            if badge:
                # update awarded date
                badge.awarded_date = timezone.now()
                badge.save()
            # if the user does not have an active badge
            else:
                badge = GreatServiceProviderBadge.objects.create(
                    owner=Owner.objects.get(pk=pk),
                    awarded_date=timezone.now()
            )


@receiver(timeline)
@receiver(profile_detail, sender=Profile)
@receiver(offer_detail, sender=OfferDetailView)
def award_Newcomer_badge(sender, owner_pk, **kwargs):
    print('Checking Newcomer badges...')
    for pk in owner_pk:
        # check if the user has an active badge
        try:
            badge = NewcomerBadge.objects.get(owner__pk=pk, is_active=True)
            # check if the user still deserves the badge
            active = badge.is_badge_active
        # if the user does not have a badge
        except NewcomerBadge.DoesNotExist:
            # check if the user deserves the badge
            award = NewcomerBadge.should_award(pk)
            if award:
                badge = NewcomerBadge.objects.create(
                    owner=Owner.objects.get(pk=pk),
                    awarded_date=timezone.now()
                )


@receiver(timeline)
@receiver(profile_detail, sender=Profile)
@receiver(offer_detail, sender=OfferDetailView)
def award_CB_badge(sender, owner_pk, **kwargs):
    print('Checking Community Builder badges...')
    for pk in owner_pk:
        # check if the user deserves a badge
        award = CommunityBuilderBadge.should_award(pk)
        if award:
            # check if the user has a badge already
            try:
                badge = CommunityBuilderBadge.objects.get(owner__pk=pk)
                # check if the badge is active
                badge = badge if badge.is_badge_active else None
            except CommunityBuilderBadge.DoesNotExist:
                badge = None

            # if user has an active badge
            if badge:
                # update awarded date
                badge.awarded_date = timezone.now()
                badge.save()
            # if the user does not have an active badge
            else:
                badge = CommunityBuilderBadge.objects.create(
                    owner=Owner.objects.get(pk=pk),
                    awarded_date=timezone.now()
                )
    