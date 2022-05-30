from django.shortcuts import render
from offers.models import Offer
from django.http import JsonResponse
from django.contrib.auth.models import User
from actstream import feeds
from actstream.models import model_stream
from sharity.services import SharityOfferRecommender
import json
import random
import datetime


def home(request):

    # Number of unread notification is send to main page
    if request.user.is_authenticated:
        offers = Offer.objects.filter(amendment_deadline__lte=datetime.datetime.now() + datetime.timedelta(days=1))
        result = SharityOfferRecommender.recommend(offers, request.user, 3)
        unreadNote = request.user.receiverID.filter(status='Unread').count
        stream = model_stream(request.user)
        for i in stream:
            print(vars(i))

        return render(request, 'home_with_activity.html', {'offers': result, 'notes': unreadNote,"stream":stream})
    else:
        result = list(Offer.objects.all())
        unreadNote = ""

        return render(request, 'home.html', {'offers': random.sample(result, 3), 'notes': unreadNote})


def notificationcount(request):

    if request.user.is_authenticated:
        unreadNoteCount = request.user.receiverID.filter(status='Unread').count()
    else:
        unreadNoteCount = ""

    return JsonResponse({'count':unreadNoteCount})


def activity_feed(request):
    return render(request, 'activity_feed.html')

