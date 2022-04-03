
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import  MyRegisterForm

# Models and Formed used in this app
from .models import  Profile 

# Sign-in Functionality
def signinPage(request):
    
    # If user is already autheticated there is no need for sign-in, so page is redirected to home
    if request.user.is_authenticated:
        return redirect('home')
    
    # When info is entered at the sign-in page, username and password is validated
    # If they match, then user is autenticated, otherwise error message is rendered
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        errorMessage = ""

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
    context = {'error':errorMessage}
    return render(request, 'member/signin.html', context)

# This is basic sign-out feature
def signOut(request):
    logout(request)
    return redirect('home')

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
            login(request,user)
            
    # Django's default user model is used for User management. Therefore for further information about user is stored at Profile model
    # At quick signup, Location is a mandatory field from Profile model
    # New profile for this user is created and saved after adding Location information 
            newProfile = Profile.objects.create(user=user, userLocation=request.POST.get('location'))
            newProfile.save()
    
    # After user is created, page is redirected to home page
    # Error is rendered in case there is problem in sign-up process 
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    
    return render(request, 'landing/signup.html', {'form':form})


# This is getting user information
def userProfile(request, userKey):
    user = User.objects.get(username=userKey)
    context = {'user':user, }
    return render(request, 'landing/profile.html', context) 

# This is for updating user profile
# Login is required to see details of services 

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

        myProfile.userLocation = request.POST.get('location')
        myProfile.userDetails = request.POST.get('userDetails')
        myProfile.userInterests = request.POST.get('userInterests')
        myProfile.userSkills = request.POST.get('userSkills')
        myProfile.userBadge = request.POST.get('userBadge')

        if request.FILES.get('picture') is not None:
            myProfile.userPicture = request.FILES.get('picture')
        myProfile.save()

        return redirect('home')
        
    context = {'form':form,'myProfile':myProfile, 'user':user}
    return render(request, 'landing/updateprofile.html', context)

def home(request):
    context = {'info':''}
    return render(request, 'landing/home.html', context)
