from django.contrib import admin
from .models import Task, Notification, UserProfile

# Register your models here.

admin.site.register(Task)
admin.site.register(Notification)
admin.site.register(UserProfile)