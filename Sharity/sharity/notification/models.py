from django.db import models
import uuid
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from offers.models import Offer


# Create your models here.
# This object is to keep information for notifications during processes
class Notification(models.Model):
    
    # There are 2 states for requests
    NOTE_STATUS = [
        ("Unread", "Unread"),
        ("Read", "Read"),
    ]

    # noteID is created as unique id from UUID object
    noteID = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    # serviceID has a One-to-Many relation with Service object: a service is one service from many Services
    serviceID = models.ForeignKey(Offer, on_delete=models.CASCADE, null=True)
    # receiverID has a One-to-Many relation with User object: a notificiation is received by one user from many Users
    receiverID = models.ForeignKey(User, related_name='receiverID', on_delete=models.CASCADE)
    noteContent = models.CharField(max_length=1000)
    status = models.CharField(max_length=1000,choices=NOTE_STATUS,default='Unread')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # user_has_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.noteID}'
