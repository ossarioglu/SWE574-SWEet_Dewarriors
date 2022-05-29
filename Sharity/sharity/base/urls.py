from django.urls import path
from . import views
from member import views as memberview
from apply import views as applyview
from assign import views as assignview
from notification import views as notificationview
from feedback import views as feedbackview
from offers import views as offerview


urlpatterns = [
    path('', views.home, name="home"),
    path('login/', memberview.signinPage, name="login"),
    path('logout/', memberview.signOut, name="logout"),
    path('signup/', memberview.signUp, name="signup"),
    path('member/follow/', memberview.followUser, name="follow"),
    path('member/unfollow/', memberview.unfollowUser, name="unfollow"),
    # path('member/<str:userKey>/', memberview.userProfile, name ="profile"),
    path('member/<str:userKey>/', memberview.ProfileDetailView.as_view(), name ="profile"),
    path('myofferings/', memberview.listofferings, name="listmyofferings"),
    path('member/<str:userKey>/update/', memberview.updateProfile, name ="updateProfile"),
    path('login/', memberview.signinPage, name="handshake"),
    path('login/', memberview.signinPage, name="notifications"),
    path('apply/<uuid:sID>/', applyview.requestOffer, name="offers.apply"),
    path('cancelapply/<uuid:rID>/', applyview.deleteRequest, name="offers.apply.cancel"),
    path('assign/<uuid:rID>/', assignview.assignService, name="offers.assign"),
    path('assignoffer/<uuid:ofnum>/', assignview.assigning, name="offers.listassign"),
    path('offers/update/<uuid:sID>/', offerview.OfferUpdateView.as_view(), name='offers.update'),
    path('offers/delete/<uuid:sID>/', offerview.deleteOffer, name='offers.delete'),
    path('notification/getall/', views.notificationcount, name='ajax_load_results'),
    path('activity/feed/', views.activity_feed, name='activity.feed'),
    # URLs for notification process: listing and updating
    path('notification/', notificationview.notifications, name ="notifications"), 
    path('notification/<str:nID>/', notificationview.changeNote, name ="changeNote"), 

# URLs for handshaking process: listing and confirming assignments
    path('handshake/', assignview.handshaking, name ="handshake"), 
    path('confirm/<str:asNum>/', feedbackview.confirmation, name ="confirmService"), 


]
