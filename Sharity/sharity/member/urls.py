from django.urls import path
from . import views

urlpatterns = [
    path('member/', views.home, name ="profile"),
    
]