from django.urls import path

from . import views

urlpatterns = [
    path('new/', views.OfferCreateView.as_view(), name='offers.create'),
]