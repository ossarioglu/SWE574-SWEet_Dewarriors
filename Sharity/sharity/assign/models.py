
from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from Sharity.sharity.apply.models import Application
# unique identifiers for objects are created with this 
import uuid

# This object is to keep information for notifications during processes
class Assignment(models.Model):
    
    # There are 3 states for requests
    ASSIGNMENT_STATUS = [
        ("Open", "Open"),
        ("Confirmed by provider", "Confirmed by provider"),
        ("Confirmed by receiver", "Confirmed by receiver"),
        ("Closed", "Closed"),
    ]
    
    # assignID is created as unique id from UUID object
    assignID = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    # requestID has a One-to-Many relation with Request object: a request can be assigned from one reques from many Request
    requestID = models.ForeignKey(Application, on_delete=models.CASCADE)
    # approverID has a One-to-Many relation with User object: a assignment is approved by one user from many Users
    approverID = models.ForeignKey(User, related_name='approverForAssignementID',  on_delete=models.CASCADE)
    # requesterID has a One-to-Many relation with User object: a assignment is requested by one user from many Users    
    requesterID = models.ForeignKey(User, related_name='requesterForAssignementID',  on_delete=models.CASCADE)
    serviceType = models.CharField(max_length=100)
    status = models.CharField(max_length=100,choices=ASSIGNMENT_STATUS,default='Open')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.assignID}'