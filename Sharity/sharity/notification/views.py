from django.shortcuts import render
from .models import Notification
# from django.db.models import Q


# This is for listing notifications
# Login is required to see details of services
def notifications(request):
    myNotes = request.user.receiverID.filter()
    context = {'myNotes':myNotes }
    return render(request, 'notification/notifications.html', context)

# This is for updating status of notifications between 'Read' and 'Unread'
# Login is required to see details of services

def changeNote(request, nID):
    myNotes = request.user.receiverID.filter()
    myNote = Notification.objects.get(noteID=nID)
    
    if myNote.status == "Unread":
       myNote.status = "Read"
    myNote.delete()

    context = {'myNotes':myNotes }
    return render(request, 'notification/notifications.html', context)

# def deleteNote(request, nID):
#     myNote = Notification.objects.get(noteID=nID)
#
#     myNote.delete()