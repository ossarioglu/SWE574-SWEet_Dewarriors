import random
from django.shortcuts import render
from offers.models import Offer


def home(request):
    result = list(Offer.objects.all().exclude(owner=request.user))
    return render(request,'home.html', {'offers': random.sample(result, 3)})


