from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserMessagesMainView.as_view(), name='usermessages.main'),
    path('new-message/', views.SendMessageView.as_view(), name='usermessages.create'),
    path('ajax/inbox/', views.InboxView.as_view(), name='usermessages.inbox'),
    path('ajax/message-detail/', views.MessageDetailView.as_view(), name='usermessages.detail'),
    path('ajax/sent/', views.SentMessagesView.as_view(), name='usermessages.sent'),
    path('ajax/deleted/', views.DeletedMessagesView.as_view(), name='usermessages.deleted'),
    path('ajax/message-delete/', views.MessageDeleteView.as_view(), name='usermessages.delete'),
    path('ajax/update-is-read/', views.UserMessageReadUpdateView.as_view(), name='usermessages.update'),
    path('ajax/get-num-of-unreads-mails/', views.GetNumOfUnreadMailsAjaxView.as_view(), name='usermessages.unread'),
    path('ajax/restore-deleted-message/', views.RestoreDeletedMessageView.as_view(), name='usermessages.restore')
]