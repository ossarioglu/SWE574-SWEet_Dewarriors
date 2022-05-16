import uuid
from django.http import HttpResponse
from django.shortcuts import redirect, render
from apply.models import Application
from assign.models import Assignment
from offers.models import Offer
from notification.models import Notification


# This is for listing assingments for the services
# Login is required to see details of services 

#@login_required(login_url='login')
def assigning(request, ofnum):
    offer = Offer.objects.get(uuid=ofnum)
    application = Application.objects.filter(serviceID=ofnum)
    allAccepted = Application.objects.filter(status='Accepted').filter(serviceID=offer).count()
    
    # Remaning capacity is sent to frontend to avoid more assignments than capacity
    remainingCapacity = offer.participant_limit - allAccepted

    context = {'offers':offer, 'applications':application, "remainingCapacity":remainingCapacity}
    
    #This needs to be updated based on assignment Front-end
    return render(request, 'assign/assignment.html', context)

# This is for accepting requests and assinging users for the services
# Login is required to see details of services

#@login_required(login_url='login')
def assignService(request, rID):

    # Information application to be assigned is retrieved
    myRequest = Application.objects.get(requestID=rID)

    # Application is processed if it's still in 'Inprocess' state
    # New assignment object is created for this application
    if myRequest.status == 'Inprocess':
        newassignment = Assignment.objects.create(
                requestID=myRequest, 
                approverID=request.user, 
                requesterID=myRequest.requesterID, 
                serviceType=myRequest.serviceType, 
                status="Open"
            )    
       
        # When assignment is done status for service is updated as 'Assigned', and application status is updated as 'Accepted'
        if newassignment:

            newassignment.requestID.serviceID.status = 'Assigned'
            newassignment.save()
            
            myRequest.status = 'Accepted'
            myRequest.save()

            # Remaining capacity is calculated by deducting all accepted request.

            allAccepted = Application.objects.filter(status='Accepted').filter(serviceID=myRequest.serviceID).count()
            remainingCapacity = newassignment.requestID.serviceID.participant_limit - allAccepted

            # New notification is created for requesters to inform that the application is accepted, and request is approved
            newnote = Notification.objects.create(
                    serviceID=myRequest.serviceID, 
                    receiverID=myRequest.requesterID, 
                    noteContent=request.user.username
                                +' approved your request for '
                                + myRequest.serviceID.title, 
                    status='Unread'
               )
            if newnote:

                # After the assignment, if there is no availbe capacility, all 'Inprocess' applications' status are updated as 'Rejected'
                # Credits for these applications are released back
                # A notification is sent to requester to inform than application is rejected due to capacity constraint

                if remainingCapacity == 0:
                    openRequests = Application.objects.filter(status='Inprocess').filter(serviceID=myRequest.serviceID)
                    
                    for openRqst in openRequests:
                        openRqst.status = 'Rejected'
                        openRqst.save()

                        # Credits given back
                        creditNeeded = 0
                        if openRqst.serviceID.serviceType == "Offering":
                            creditNeeded = openRqst.serviceID.duration
                        blkQnt= creditNeeded
                        openRqst.requesterID.profile.blockCredit(+blkQnt)
                        openRqst.requesterID.profile.save()
                        
                        # Notification for rejection
                        newnote = Notification.objects.create(
                                serviceID=openRqst.serviceID, 
                                receiverID=openRqst.requesterID, 
                                noteContent=request.user.username
                                            +' could not acceept your request for '
                                            + myRequest.serviceID.title
                                            +' due to capacity constraints',
                                status='Unread'
                            )
                
                # User is sent back to assignment page to see updates.
                application = Application.objects.filter(serviceID=myRequest.serviceID)
                context = {'offers':myRequest.serviceID, "applications":application, "remainingCapacity":remainingCapacity}
                return render(request, 'assign/assignment.html', context)
        else:
            return HttpResponse("A problem occured. Please try again later")
    else:
        return redirect('home')


# This is for listing all approved assignment for both provider and receiver
# Login is required to see details of services
#@login_required(login_url='login')
def handshaking(request):
    providedAssignment = Assignment.objects.filter(approverID=request.user)
    receivedAssignment = Assignment.objects.filter(requesterID=request.user)

    context = {'providedAssignments':providedAssignment, "receivedAssignments":receivedAssignment}
    return render(request, 'assign/handshake.html', context)
