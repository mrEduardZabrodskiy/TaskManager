from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Task(models.Model):
    
    class Status(models.TextChoices):
        WAITING = 'W', 'Waiting'
        STARTED = 'S', 'Started'
        COMPLITED = 'C', 'Completed'
    
    class Priority(models.TextChoices):
        LOW = 'L', 'Low'
        MEDIUM = 'M', 'Medium'
        HIGH = 'H', 'High'
    
        
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(max_length=2000, blank=True)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.WAITING)
    priority = models.CharField(max_length=1, choices=Priority.choices, default=Priority.LOW)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)
    
    
    
    class Meta:
        ordering = ['-created', 'author']
        indexes = [
            models.Index(fields=['-created']),
        ]
    
    def get_absolute_url(self):
        return self.title
        #return reverse('task:task_update', args=[self.created.year, self.slug])