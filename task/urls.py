from django.urls import path
from . import views

urlpatterns = [
    path('task-list/', views.task_list, name='task_list'),
    path('task-create/', views.task_create, name='task_create'),
    path('task-update/<int:pk>', views.task_update, name='task_update'),
    path('task-update/<int:pk>/<str:status>', views.task_update, name='task_update'),
    path('task-delete/<int:pk>', views.task_delete, name='task_delete'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('register/', views.register_view, name='register_view'),
]