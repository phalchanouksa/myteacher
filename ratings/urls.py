from django.urls import path
from . import views

urlpatterns = [
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
]
