from math import radians, cos, sin, asin, sqrt
import json
import random
from badges.models import *
def distance(lat1, lat2, lon1, lon2):
     
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
      
    # calculate the result
    return(c * r)

def get_lat(loc):
    payload = json.loads(str(loc).replace("\\'", '"'))
    return payload['geometry']['location']['lat']

def get_long(loc):
    payload = json.loads(str(loc).replace("\\'", '"'))
    return payload['geometry']['location']['lng']

def order_offers(offers):
    newcomers = []
    greatserviceproviders = []
    mastereventorganizers = []
    communitybuilders = []
    no_badge = []

    for offer in offers:
        if any(isinstance(badge, GreatServiceProviderBadge) for badge in offer.owner_badges):
            greatserviceproviders.append(offer)
        elif any(isinstance(badge, MasterEventOrganizerBadge) for badge in offer.owner_badges):
            mastereventorganizers.append(offer)
        elif any(isinstance(badge, CommunityBuilderBadge) for badge in offer.owner_badges):
            communitybuilders.append(offer)
        elif any(isinstance(badge, NewcomerBadge) for badge in offer.owner_badges):
            newcomers.append(offer)
        else:
            no_badge.append(offer)

    ordered_result = []
    while len(newcomers) + len(greatserviceproviders) + len(mastereventorganizers) + len(communitybuilders) + len(no_badge) > 0:
        if len(newcomers) > 0:
            newcomer_choice = random.choice(newcomers)
            ordered_result.append(newcomer_choice)
            newcomers.remove(newcomer_choice)

        if len(communitybuilders) > 0:
            cb_choice = random.choice(communitybuilders)
            ordered_result.append(cb_choice)
            communitybuilders.remove(cb_choice)

        if len(no_badge) > 0:
            no_badge_choice = random.choice(no_badge)
            ordered_result.append(no_badge_choice)
            no_badge.remove(no_badge_choice)

        if len(mastereventorganizers) > 0:
            meo_choice = random.choice(mastereventorganizers)
            ordered_result.append(meo_choice)
            mastereventorganizers.remove(meo_choice)
        
        if len(greatserviceproviders) > 0:
            gsp_choice = random.choice(greatserviceproviders)
            ordered_result.append(gsp_choice)
            greatserviceproviders.remove(gsp_choice)
    
    return ordered_result