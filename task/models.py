from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Task(models.Model):
    
    class Status(models.TextChoices):
        WAITING = '1W', 'Waiting'
        STARTED = '2S', 'Started'
        COMPLITED = '3C', 'Completed'
    
    class Priority(models.TextChoices):
        LOW = '1L', 'Low'
        MEDIUM = '2M', 'Medium'
        HIGH = '3H', 'High'
    
        
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(max_length=2000, blank=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.WAITING)
    priority = models.CharField(max_length=2, choices=Priority.choices, default=Priority.LOW)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)
    
    
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created', 'author']),
        ]
    
    def get_absolute_url(self):
        return self.title
        #return reverse('task:task_update', args=[self.created.year, self.slug])
    

class Notification(models.Model):
    title = models.CharField(max_length=150)
    url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='users_images', blank=True, default='users_images/user.png')
    email_confirm_status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username