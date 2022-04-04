from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.

# Profile is the object keeping information of users
# This object is an addition to Django's User object. It has additionla information that User object does't have

class Profile(models.Model):
    # There are 3 types of user
    USER_TYPES = [
        ("user", "user"),
        ("admin", "admin"),
        ("mentor", "mentor"),
    ]

    # user has one-to-one relatiınship with User object
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    userType = models.CharField(max_length=10, choices=USER_TYPES, default='user')
    # user rating is kept at this field
    userReputation = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    # This fields needs to be updated when admin service is created
    creditAmount = models.PositiveIntegerField(editable=True, default=5)
    userDetails = models.TextField(max_length=1000, null=True)
    userSkills = models.TextField(max_length=1000, null=True)
    userInterests = models.TextField(max_length=1000, null=True)
    userLocation = models.CharField(max_length=100)
    userBadge = models.TextField(max_length=100, null=True, default="None")

    userPicture = models.ImageField(upload_to='Profiles', null=True, default="male.png")
    # credits are blocked at this field for applied services that are not concluded
    creditInprocess = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}'

    # This is the method to update user's credit Amount
    # Credit amount is restristed to be max 15 in order to motivate user's to get services as well (not only providing)
    def updateCredit(self, amount):
        self.creditAmount += amount
        if self.creditAmount > 15:
            self.creditAmount = 15
        return True

    def blockCredit(self, amount):
        self.creditInprocess += amount

    def checkCredit(self, amount):
        return ((self.creditAmount + self.creditInprocess) >= amount)
