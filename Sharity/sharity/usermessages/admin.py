from django.contrib import admin
from .models import UserMessage, UserInbox

# Register your models here.
admin.site.register([UserMessage, UserInbox])