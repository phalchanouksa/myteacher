from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('chat/<int:partner_id>/', views.chat_detail, name='chat_detail'),
    path('unread-count/', views.get_unread_count, name='get_unread_count'),
] 