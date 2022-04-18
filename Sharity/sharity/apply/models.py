from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from offers.models import Offer

# unique identifiers for objects are created with this 
import uuid


# This object is to keep information for applications to services
class Application(models.Model):

    # There are 3 states for requests
    REQUEST_STATUS = [
        ("Inprocess", "Inprocess"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]
    # requestID is created as unique id from UUID object
    requestID = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    # serviceID has a One-to-Many relation with Service object: a service is one service from many Services
    serviceID = models.ForeignKey(Offer, on_delete=models.CASCADE)
    # requesterID has a One-to-Many relation with User object: a service is requested by one user from many Users
    requesterID = models.ForeignKey(User, on_delete=models.CASCADE)
    serviceType = models.CharField(max_length=100)
    status = models.CharField(max_length=100,choices=REQUEST_STATUS,default='Open')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.requestID}'