import uuid
from django.http import HttpResponse
from django.shortcuts import redirect, render
from prompt_toolkit import Application

from offers.models import Offer

# This is for user's applications to service. When user apply for a service, this is triggered. 
# Request for service is done with posting service's unique id
# Login is required to see details of services 

#@login_required(login_url='login')
def requestOffer(request, sID):
    offer = Offer.objects.get(uuid=sID)
    
    # This variable is used for blocking or deducting credits of users
    # As default it's set as 0 for Events, and if service is an Offering then, it's updates as the duration of activity
    creditNeeded = 0
    if offer.Type == "Service":
        creditNeeded = offer.duration

    # User can apply a service only if there is enough credit
    # Since user's credits are blocked at creditInprocess for ongoing services (Open requests, accepted application)
    # available credit is calculated by summing current creditAmount and creditInprocess
    # Events are free activities, so user can apply any Event even if there is no available credit
    if (request.user.profile.creditAmount + request.user.profile.creditInprocess) >= creditNeeded:

        # If user didn't apply the service before, then new request is created
        if not Application.objects.filter(serviceID=offer).filter(requesterID=request.user).exists():
            
            # Status of new requests are Inprocess
            newrequest = Application.objects.create(serviceID=offer, requesterID=request.user, serviceType=offer.Type, status='Inprocess')
            if newrequest:
                
                # When a request is created, credits of users are blocked by calling blockCredit method of Profile object

                blkQnt = creditNeeded
                request.user.profile.blockCredit(-blkQnt)
                request.user.profile.save()

                # A notification is created for service provider to inform that user is applied to this service
    #            newnote = Notification.objects.create(
    #                serviceID=offer, 
    #                receiverID=offer.providerID, 
    #                noteContent=request.user.username+' applied for ' 
    #                            + offer.keywords,
    #                            status='Unread'
    #                )

                # After notification is created, user is sent back to services information page
     #           if newnote:
     #               application = Requestservice.objects.filter(serviceID=sID).filter(requesterID=request.user)
     #               context = {'offers':Offering.objects.get(serviceID=sID), "applications":application}
     #               return render(request, 'landing/offerings.html', context)
            else:
                return HttpResponse("A problem occured. Please try again later")
        else:
            application = Application.objects.filter(serviceID=sID).filter(requesterID=request.user)
            context = {'offers':Offer.objects.get(uuid=sID), "applications":application}
            return render(request, 'landing/offerings.html', context)
    
    # If user doesn't have enough credit, this state is sent to front-end as a message variable during render
    else:
        textMessage = "Not Enough Credit"
        application = Application.objects.filter(serviceID=sID).filter(requesterID=request.user)
        context = {'offers':Offer.objects.get(uuid=sID), "applications":application, "textMessage":textMessage}
        return render(request, 'landing/offerings.html', context)

# This is for cancelling user's applications.
# Cancellation for request is done with request's unique id
# Login is required to see details of services 

#@login_required(login_url='login')

def deleteRequest(request, rID):
    
    #Information for the queried reques is retrieved.
    reqSrvs = Application.objects.get(requestID=rID)
    offer = reqSrvs.serviceID
    providerUser = offer.owner
    
    #Credit calculation is done, Events: 0, Offerings:Duration
    creditNeeded = 0
    if offer.Type == "Service":
        creditNeeded = offer.duration
    blkQnt= creditNeeded

    requestingUser = request.user
    context = {'obj':reqSrvs, 'providerUser':providerUser,'requestingUser':requestingUser, 'blockedQnt':blkQnt}

    if request.user != reqSrvs.requesterID:
        return HttpResponse('You are not allowed to delete this offer')

    #If user posts cancellation for request, request is deleted from database
    # Credits blocked for the event is given back to user by updating inprocessCredits 
    if request.method == 'POST':
        reqSrvs.delete()

        blkQnt = creditNeeded
        request.user.profile.blockCredit(+blkQnt)
        request.user.profile.save()

        return redirect('home')
    return render(request, 'landing/cancelRequest.html', context)