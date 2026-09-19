from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('task/new/', views.task_create, name='task_create'), # Form to create a task
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/complete/', views.complete_task, name='complete_task'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'), # Delete a task
]