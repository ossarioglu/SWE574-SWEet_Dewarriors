from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from offers.models import Offer

# unique identifiers for objects are created with this 
import uuid

# Create your models here.

# This object is to keep information on feedbacks while confirming services are done
class Feedback(models.Model):
    
    # There are 5 rating options
    FEEDBACK_RATING = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]
    
    # feedbackID is created as unique id from UUID object
    feedbackID = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    #serviceID has a One-to-Many relation with Service object: a service is one service from many Services
    serviceID = models.ForeignKey(Offer,related_name='feedbackForService', on_delete=models.CASCADE)
    # giverID has a One-to-Many relation with User object: a feedback is given from a user from many Users
    giverID = models.ForeignKey(User, related_name='feedbackGiverID', on_delete=models.CASCADE)
    # takerID has a One-to-Many relation with User object: a feedback is taken from a user from many Users
    takerID = models.ForeignKey(User, related_name='feedbackReceiverID', on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveIntegerField(editable=True,choices=FEEDBACK_RATING, default=1)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.feedbackID}'