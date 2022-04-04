from django.urls import path
from . import views
from member import views as memberview

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', memberview.signinPage, name="login"),
    path('logout/', memberview.signOut, name="logout"),
    path('signup/', memberview.signUp, name="signup"),
    path('member/<str:userKey>/', memberview.userProfile, name ="profile"),
]
