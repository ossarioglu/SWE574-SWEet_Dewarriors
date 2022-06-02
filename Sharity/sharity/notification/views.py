from django.shortcuts import render
from .models import Notification


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
    
    if myNote.status == "Read":
        myNote.status = "Unread"
    else:
        myNote.status = "Read"
    myNote.save()

    context = {'myNotes':myNotes }
    return render(request, 'notification/notifications.html', context)
