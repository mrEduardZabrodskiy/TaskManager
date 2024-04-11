from django.urls import path
from . import views

urlpatterns = [
    path('task-list/', views.task_list, name='task_list'),
    path('task-list/<str:sort>', views.task_list, name='task_list'),
    path('task-list/<str:filter>', views.task_list, name='task_list'),
    path('task-create/', views.task_create, name='task_create'),
    path('task-update/<int:pk>', views.task_update, name='task_update'),
    path('task-update/<int:pk>/<str:status>', views.task_update, name='task_update'),
    path('task-delete/<int:pk>', views.task_delete, name='task_delete'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('register/', views.register_view, name='register_view'),
    path('account/<int:pk>', views.account, name='account'),
    path('settings/', views.settings, name='settings'),
    path('password-change/', views.password_change, name='password_change'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/<slug:uidb64>/<slug:token>', views.password_reset_confirm, name='password_reset_confirm'),
]