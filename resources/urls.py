from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('test/', views.test_view, name='test'),
    path('', views.ResourceListView.as_view(), name='list'),
    path('create/', views.ResourceCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ResourceDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ResourceUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ResourceDeleteView.as_view(), name='delete'),
    path('<int:pk>/like/', views.ResourceLikeView.as_view(), name='like'),
    path('<int:pk>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
]
