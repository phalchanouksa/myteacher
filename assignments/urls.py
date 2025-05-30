from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    # Assignment URLs
    path('', views.AssignmentListView.as_view(), name='assignment-list'),
    path('create/', views.AssignmentCreateView.as_view(), name='assignment-create'),
    path('<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment-detail'),
    path('<int:pk>/update/', views.AssignmentUpdateView.as_view(), name='assignment-update'),
    path('<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='assignment-delete'),
    
    # Submission URLs
    path('<int:pk>/submit/', views.submit_assignment, name='assignment-submit'),
    path('submission/<int:pk>/grade/', views.grade_submission, name='submission-grade'),
    path('submission/<int:pk>/download/', views.download_submission, name='submission-download'),
]
