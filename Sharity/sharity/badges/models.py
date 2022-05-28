from django.db import models
from datetime import timedelta
from django.utils import timezone
from offers.models import Offer
from member.models import Profile
from apply.models import Application
from django.db.models import Q

# Create your models here.
class UserBadge(models.Model):
    # owner = models.ForeignKey('member.Owner', on_delete=models.CASCADE, related_name='badges')
    awarded_date = models.DateTimeField()
    award_end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override award_end_date"""
        self.award_end_date = self.awarded_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    @property
    def is_badge_active(self):
        if timezone.now() > self.award_end_date:
            self.is_active = False
            self.save()
        return self.is_active


class CommunityBuilderBadge(UserBadge):
    """Those who take at least as many offers from newcomers as the number of threshold in the last 30 days"""
    owner = models.OneToOneField('member.Owner', on_delete=models.CASCADE, related_name='CBbadge')
    threshold = 5

    def __str__(self):
        return self.__class__.__name__ + ' owned by ' + self.owner.username

    @staticmethod
    def should_award(owner_pk):
        qs = Application.objects.filter(requesterID__pk=owner_pk, status='Accepted', serviceType='1').select_related('serviceID').prefetch_related('serviceID__owner')
        count = 0
        for a in qs:
            if hasattr(a.serviceID.owner, 'Nbadge') and a.serviceID.created_at > timezone.now() - timedelta(days=30):
                count += 1
        if count >= CommunityBuilderBadge.threshold:
            return True
        return False

    @property
    def is_badge_active(self):
        return super().is_badge_active


class MasterEventOrganizerBadge(UserBadge):
    """Those who have offered at least as many events as the number of threshold in the last 30 days"""
    owner = models.OneToOneField('member.Owner', on_delete=models.CASCADE, related_name='MEObadge')
    threshold = 10

    def __str__(self):
        return self.__class__.__name__ + ' owned by ' + self.owner.username
        
    @staticmethod
    def get_filters():
        filters = Q()

        offer_logic = {
            'created_at__gt': timezone.now() - timedelta(days=30),
            'type': 2
        }
        for key, value in offer_logic.items():
            filters.add(Q(**{key: value}), Q.AND)

        return filters

    @staticmethod
    def should_award(owner_pk):
        qs = Offer.objects.filter(MasterEventOrganizerBadge.get_filters()).filter(owner__pk=owner_pk)
        if len(qs) >= MasterEventOrganizerBadge.threshold:
            return True
        return False

    @property
    def is_badge_active(self):
        return super().is_badge_active


class GreatServiceProviderBadge(UserBadge):
    """Those who have offered at least as many services as the number of threshold while having average reputation score of 4/5"""
    owner = models.OneToOneField('member.Owner', on_delete=models.CASCADE, related_name='GSPbadge')
    threshold = 10
    score = 4

    def __str__(self):
        return self.__class__.__name__ + ' owned by ' + self.owner.username

    @staticmethod
    def get_filters():
        filters = Q()

        offer_logic = {
            'created_at__gt': timezone.now() - timedelta(days=30),
            'type': 1
        }
        for key, value in offer_logic.items():
            filters.add(Q(**{key: value}), Q.AND)
        
        return filters

    @staticmethod
    def should_award(owner_pk):
        qs = Offer.objects.filter(GreatServiceProviderBadge.get_filters()).filter(owner__pk=owner_pk).prefetch_related('feedbackForService')
        feedbacks = [i.feedbackForService.all()[0] for i in qs if len(i.feedbackForService.all()) > 0]
        scores = [j.rating for j in feedbacks]
        try:
            avg_score = sum(scores) / len(scores)
            if len(qs) >= GreatServiceProviderBadge.threshold and avg_score >= GreatServiceProviderBadge.score:
                return True
            return False
        except ZeroDivisionError:
            return False

    @property
    def is_badge_active(self):
        return super().is_badge_active


class NewcomerBadge(UserBadge):
    """Users that haven't reached 1 month since their registration"""
    owner = models.OneToOneField('member.Owner', on_delete=models.CASCADE, related_name='Nbadge')
    threshold = timedelta(days=30)

    def __str__(self):
        return self.__class__.__name__ + ' owned by ' + self.owner.username

    @staticmethod
    def should_award(owner_pk):
        profile = Profile.objects.get(user__pk=owner_pk)
        if profile.user.date_joined > timezone.now() - timedelta(days=30):
            return True
        return False

    @property
    def is_badge_active(self):
        return super().is_badge_active