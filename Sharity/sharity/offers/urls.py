from django.urls import path

from . import views

urlpatterns = [
    path('new/', views.OfferCreateView.as_view(), name='offers.create'),
    path('<uuid:pk>/', views.OfferDetailView.as_view(), name='offers.detail'),
    path('timeline/', views.OfferListView.as_view(), name='offer.list'),
]
