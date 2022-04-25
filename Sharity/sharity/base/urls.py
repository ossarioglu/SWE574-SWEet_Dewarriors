from django.urls import path
from . import views
from member import views as memberview
from apply import views as applyview
from assign import views as assignview

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', memberview.signinPage, name="login"),
    path('logout/', memberview.signOut, name="logout"),
    path('signup/', memberview.signUp, name="signup"),
    path('member/<str:userKey>/', memberview.userProfile, name ="profile"),
    path('login/', memberview.signinPage, name="notifications"),
    path('login/', memberview.signinPage, name="handshake"),
    path('apply/<str:sID>/', applyview.requestOffer, name="offers.apply"),
    path('cancelapply/<uuid:rID>/', applyview.deleteRequest, name="offers.apply.cancel"),
    path('assign/<str:rID>/', assignview.assignService, name="offers.assign"),

]
