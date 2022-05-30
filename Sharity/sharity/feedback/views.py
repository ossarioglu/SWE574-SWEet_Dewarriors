from django.shortcuts import render

import uuid
from django.http import HttpResponse
from django.shortcuts import redirect, render
from apply.models import Application
from notification.models import Notification
from assign.models import Assignment
from feedback.models import Feedback
from apply.models import Application

# This is for handshaking, and confirming the service is done, and feedbacks are given to each party. 
# Login is required to see details of services
#@login_required(login_url='login')
def confirmation(request, asNum):
    
    # Information is retreived for relevant assignment
    myAssignment = Assignment.objects.get(assignID=asNum)

    # User posts any input for confirmation, these steps are triggered
    if request.method == 'POST':

        # This block is to define whether posting user is receiver or provider for the service
        # Based on the user, state of assignment will be updated
        # State is also affected for previous state of the assignment
        # For instance, if assignment was an 'Open' assignment, meaning there was no process before, it's stated is updated as:
        #  - 'Confirmed by provider' if posting user is provider of service
        #  - 'Confirmed by receiver' if posting user is receiver of service
        # If this assignment was already processed before, it's state becomes 'Closed'

        pID = request.user
        if myAssignment.requestID.serviceID.owner == request.user:
            rID = myAssignment.requestID.requesterID
            if myAssignment.status == 'Open':
                aStatus = "Confirmed by provider"
            elif myAssignment.status == 'Confirmed by receiver':
                aStatus = "Closed"
        else:
            rID = myAssignment.requestID.serviceID.owner
            if myAssignment.status == 'Open':
                aStatus = "Confirmed by receiver"
            elif myAssignment.status == 'Confirmed by provider':
                aStatus = "Closed"
        
        # Each user needs to give feedback with a rating to confirm the service is done, and close the assignment
        # Feedback object is created and recorded to database inline to information from the form posting
        feedback = Feedback.objects.create(
            serviceID=myAssignment.requestID.serviceID, 
            giverID=pID, 
            takerID=rID, 
            comment= request.POST.get('offerComment'),
            rating=request.POST.get('sRate')
            )
        if feedback:
            
            # Assignment status is updated
            myAssignment.status=aStatus
            myAssignment.save()

            # If an assignment is closed, this doesn't mean that service is also closed for services having more than 1 participants
            if aStatus == "Closed":

                # All requests for this service is retreived
                allRequests = Application.objects.filter(serviceID=myAssignment.requestID.serviceID)

                # We check whether there is any unclosed assignment for the service
                allAssignedClosedCheck = True
                firstLoopBreak = False
                for myRequest in allRequests:
                    checkedAssignment = Assignment.objects.filter(requestID = myRequest)
                    for chAssgn in checkedAssignment:
                        if chAssgn.status != "Closed":
                            allAssignedClosedCheck = False
                            firstLoopBreak = True
                            break
                    if firstLoopBreak: 
                            break
                
                # If status for all assignments for the service 'Closed', than state of Servie is update as 'Closed'
                if allAssignedClosedCheck:
                    myAssignment.requestID.serviceID.status = 'Closed'
                    myAssignment.requestID.serviceID.save()
                    
                    # Ratings of the users are updated based on their all historic ratings
                    myFeedback = Feedback.objects.filter(takerID=myAssignment.requestID.serviceID.owner)
                    sumRating = 0.0
                    countRating = 0
                    for feeds in myFeedback:
                        sumRating += feeds.rating
                        countRating += 1
                    myRating = sumRating / countRating

                    # Credits are now deducted given to providers
                    # Provider gets credits only for one service, not from all participants
                    creditNeeded = 0
                    if myAssignment.requestID.serviceID.get_type() == "Service":
                        creditNeeded = myAssignment.requestID.serviceID.duration
                    blkQnt= creditNeeded
    

                    myAssignment.requestID.serviceID.owner.profile.updateCredit(+blkQnt)
                    myAssignment.requestID.serviceID.owner.profile.userReputation = myRating

                    myAssignment.requestID.serviceID.owner.profile.save()

                    # Blocked Credits are now deducted from all receivers getting this service  
                    for myRequest in allRequests:
                        if myRequest.status == "Accepted":
                            myFeedback = Feedback.objects.filter(takerID=myRequest.requesterID)
                            sumRating = 0.0
                            countRating = 0
                            for feeds in myFeedback:
                                sumRating += feeds.rating
                                countRating += 1
                            myRating = sumRating / countRating
                            myRequest.requesterID.profile.updateCredit(-blkQnt)
                            myRequest.requesterID.profile.blockCredit(+blkQnt)
                            myRequest.requesterID.profile.userReputation = myRating
                            myRequest.requesterID.profile.save()    

            # Notifications are created for other parties of the assignment 
            Notification.objects.create(
                serviceID=myAssignment.requestID.serviceID, 
                receiverID=rID, 
                noteContent=request.user.username+ ' confirmed that service has happened for ' + myAssignment.requestID.serviceID.title , status='Unread')
  
        return redirect('confirmService', asNum = myAssignment.assignID )

    myFeedback = Feedback.objects.filter(serviceID=myAssignment.requestID.serviceID).order_by('-created')

    context = {'myAssignment':myAssignment, 'myFeedbacks':myFeedback }
    return render(request, 'feedback/confirm.html', context)