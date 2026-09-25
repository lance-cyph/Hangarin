from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('', views.task_list, name='task_list'),
    path('task/new/', views.task_create, name='task_create'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/edit/', views.task_update, name='task_update'),
    path('task/<int:pk>/complete/', views.complete_task, name='complete_task'),
    path('task/<int:pk>/undo/', views.undo_complete_task, name='undo_complete_task'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('subtask/<int:pk>/delete/', views.subtask_delete, name='subtask_delete'), 
    path('subtask/<int:pk>/toggle/', views.toggle_subtask, name='toggle_subtask'), 
    path('note/<int:pk>/delete/', views.note_delete, name='note_delete'),
]