from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from django.http import JsonResponse
from offers.models import Offer
from assign.models import Assignment
from apply.models import Application
from .forms import MyRegisterForm
from actstream.actions import follow, unfollow
# Models and Formed used in this app
from .models import Profile
from actstream.models import following, followers

from usermessages.models import UserInbox
from decouple import config
from badges.signals import profile_detail
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from tags.services import TagService
import json


# Sign-in Functionality
def signinPage(request):
    # If user is already autheticated there is no need for sign-in, so page is redirected to home
    if request.user.is_authenticated:
        return redirect('home')

    # When info is entered at the sign-in page, username and password is validated
    # If they match, then user is autenticated, otherwise error message is rendered
    errorMessage = ""
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            errorMessage = 'User does not exist'

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            errorMessage = 'Username or password is not matching'

    # Page information is sent to frontend
    context = {'error': errorMessage}
    return render(request, 'member/signin.html', context)


# This is basic sign-out feature
def signOut(request):
    logout(request)
    return redirect('home')


def followUser(request):
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    follow(request.user, user)
    followers_list = followers(user)
    following_list = following(user)

    followers_count = len(followers_list) if len(followers_list) > 0 else 0
    following_count = len(following_list) if len(following_list) > 0 else 0



    return JsonResponse({"followersCount": followers_count,"followingCount": following_count})


def unfollowUser(request):
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    unfollow(request.user, user)
    followers_list = followers(user)
    following_list = following(user)
    followers_count = len(followers_list) if len(followers_list) > 0 else 0
    following_count = len(following_list) if len(following_list) > 0 else 0


    return JsonResponse({"followersCount": followers_count,"followingCount": following_count})

    # This is for sign-up of new users
def signUp(request):
    # Customized form for user information is called.
    form = MyRegisterForm()
    # When user details are posted, the information is matched with User model's field
    # Mandatory fields for quick signup is Username, Password, Name and Surname, Email, and Location 
    if request.method == 'POST':
        form = MyRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            login(request, user)

            """
            Django's default user model is used for User management. 
            Therefore for further information about user is stored at Profile model
            At quick signup, Location is a mandatory field from Profile model
            New profile for this user is created and saved after adding Location information
            """
            newProfile = Profile.objects.create(user=user, userLocation=request.POST.get('location-json'))
            newProfile.save()

            # after profile is saved, an inbox for that Profile instance is created
            inbox = UserInbox.objects.create(owner=newProfile)

            # After user is created, page is redirected to home page
            # Error is rendered in case there is problem in sign-up process
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')


    return render(request, 'member/signup.html', {'form': form,"googleapis":config('GOOGLE_API_KEY')})

    # This is getting user information
def userProfile(request, userKey):
    user = User.objects.get(username=userKey)
    followers_list = followers(user)
    is_already_followed = True if len(
        list(filter(lambda x: x.username == request.user.username, followers_list))) > 0 else False

    following_list = following(user)
    followers_count = len(followers_list) if len(followers_list) > 0 else 0
    following_count = len(following_list) if len(following_list) > 0 else 0

    context = {'user': user,
               'isAlreadyFollowed': is_already_followed,
               'googleapis': config('GOOGLE_API_KEY'),
               "followersCount": followers_count,
               "followingCount": following_count}
    return render(request, 'member/profile.html', context)

class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'member/profile.html'
    model = User
    
    def get_object(self):
        user = User.objects.get(username=self.kwargs.get('userKey'))
        # This is to check whether there is a valid profile for user
        check = Profile.objects.filter(user=user)
        if  len(check) == 0:
            newProfile = Profile.objects.create(user=user)
            newProfile.save()

        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        followers_list = followers(user)
        is_already_followed = True if len(
            list(filter(lambda x: x.username == self.request.user.username, followers_list))) > 0 else False

        following_list = following(user)
        followers_count = len(followers_list) if len(followers_list) > 0 else 0
        following_count = len(following_list) if len(following_list) > 0 else 0

        providedAssignment = Assignment.objects.filter(approverID=user).filter(status='Closed')
        receivedAssignment = Assignment.objects.filter(requesterID=user).filter(status='Closed')

        context['followersCount'] = followers_count
        context['followingCount'] = following_count
        context['isAlreadyFollowed'] = is_already_followed
        context['googleapis'] = config('GOOGLE_API_KEY')
        context['handshakes'] = len(providedAssignment) + len(receivedAssignment)
        
        return context

    def dispatch(self, request, *args, **kwargs):
        # send signal for badges
        profile_detail.send(sender=Profile, owner_pk=[self.get_object().pk])
        return super().dispatch(request, *args, **kwargs)


# @login_required(login_url='login')
def updateProfile(request, userKey):
    # Information from User and Profile is retrieved for authenticated user
    user = User.objects.get(username=userKey)
    myProfile = Profile.objects.get(user=user)

    # Authenticated user's information is called to Django's default UserCreation Form
    form = UserCreationForm(instance=user)

    if request.user != user:
        return HttpResponse('You are not allowed to update this profile')

    # When information is posted, it updates the user information for User and Profile models according to form's data
    # Returns back to home page after update is done.
    if request.method == 'POST':

        user.first_name = request.POST.get('firstName')
        user.last_name = request.POST.get('lastName')
        user.email = request.POST.get('email')
        user.save()

        myProfile.userLocation = request.POST.get('location-json')
        myProfile.userDetails = request.POST.get('userDetails')
        myProfile.userInterests = request.POST.get('interests-tags-json')
        myProfile.userSkills = request.POST.get('skills-tags-json')
        # myProfile.userBadge = request.POST.get('userBadge')

        if request.FILES.get('picture') is not None:
            myProfile.userPicture = request.FILES.get('picture')

        skills_json = json.loads(myProfile.userSkills.replace("\\'", '"'))
        interests_json = json.loads(myProfile.userInterests.replace("\\'", '"'))

        tag_ids = tuple([interest['id'] for interest in interests_json]) + tuple([skill['id'] for skill in skills_json])
        wb_get_entities_response = TagService.find_by_ids(tag_ids)
        claims = []

        if 'entities' in wb_get_entities_response:
            for entity_id in wb_get_entities_response['entities']:
                for claim_id in wb_get_entities_response['entities'][entity_id]['claims']:
                    if claim_id in ['P31', 'P279', 'P361', 'P366', 'P5008', 'P5125', 'P1343', 'P3095', 'P61', 'P495', 'P1424', 'P1441']:
                        for claim in wb_get_entities_response['entities'][entity_id]['claims'][claim_id]:
                            claims.append(claim['mainsnak']['datavalue']['value']['id'])
                claims.append(entity_id)

        myProfile.claims = json.dumps(claims, separators=(',', ':'))

        myProfile.save()

        return redirect('home')


    context = {'form': form, 'myProfile': myProfile, 'user': user,'googleapis': config('GOOGLE_API_KEY') }
    return render(request, 'member/updateprofile.html', context)

def home(request):
    context = {'info': ''}
    return render(request, 'base/home.html', context)

def listofferings(request):
    myuser = request.user
    # Queried service is retreived from all services
    myOffer = Offer.objects.filter(owner=myuser)
    myApplication = Application.objects.filter(requesterID=request.user)
    allApplication = Application.objects.filter(serviceID__in=myOffer)
    closedAssignment = Assignment.objects.filter(approverID=request.user).filter(status="Closed")
    receivedAssignment = Assignment.objects.filter(requesterID=request.user).filter(status="Closed")

    offerswithapplications =[]

    for offer in myOffer:
        sub = []
        offerStatus = "open"
        itsApp = allApplication.filter(serviceID=offer)
        acceptedApp = allApplication.filter(serviceID=offer).filter(status="Accepted")
        sub.append(offer)
        sub.append(itsApp)
        sub.append(acceptedApp)
        for assignment in closedAssignment:
            if offer == assignment.requestID.serviceID:
                offerStatus = "closed"
        sub.append(offerStatus)
        offerswithapplications.append(sub)


    # Serve information, and application info is sent to front-end
    context = {'offerings': myOffer, 'applications': myApplication, 'appliedtomine':allApplication, 'offandapp':offerswithapplications, 'receivedoffers':receivedAssignment }
    return render(request, 'assign/myofferings.html', context)
