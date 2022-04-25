from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.search, name='tags.search'),
    path('<str:tag_id>/', views.find_by_id, name='tags.find_by_id'),
]
