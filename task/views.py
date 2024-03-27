from django.shortcuts import render
from .models import Task
from .forms import TaskForm, LoginForm, RegistrationForm
from django.utils.text import slugify
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.

@login_required
def task_list(request):
    print(request.POST)
    if request.method == 'POST':
        tasks = Task.objects.filter(author=request.user)\
            .filter(title__contains=request.POST['search'])
        return render(request, 'task_list.html', {'tasks': tasks})
    elif request.method == 'GET':
        tasks = Task.objects.filter(author=request.user)
        
        return render(request, 'task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_task = Task(
                title = cd['title'],
                description = cd['description'],
                slug = slugify(cd['title']),
                author = request.user
            )
            new_task.save()
        return HttpResponseRedirect(reverse('task_list'))
                    
    elif request.method == 'GET':
        form = TaskForm
        return render(request, 'task_create.html', {'form': form})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, id=pk)
    if request.method == 'POST':
        form  = TaskForm(request.POST, instance=task)
        if form.is_valid():
            #form = form.cleaned_data
            form.save()
            return HttpResponseRedirect(reverse('task_list'))
    else:
        if task.author != request.user:
            return HttpResponseRedirect(reverse('task_list'))
        else:
            form = TaskForm(instance=task)
    
    return render(request, 'task_update.html', {'form': form})

  
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, id=pk)
    if request.method == 'POST':
        Task.objects.get(id=task.id).delete()
        return HttpResponseRedirect(reverse('task_list'))
    else:
        return render(request, 'task_delete.html', {'task': task})

    
   
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('task_list'))
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                username = cd['username']
                password = cd['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect(reverse('task_list'))
                    else:
                        return HttpResponse('Account is not active')
                else:
                    # учетка не создана
                    return HttpResponseRedirect(reverse('login_view'))
        else:
            form = LoginForm
            return render(request, 'login.html', {'form': form})
    
                   
               
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login_view'))


def register_view(request):
    if request.user.is_authenticated:
        HttpResponseRedirect(reverse('task_list'))
    else:
        form = RegistrationForm
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user = User.objects.create_user(
                    username = cd['username'],
                    password = cd['password'],
                    email = cd['email']
                )
                user.save()
                # message
                return HttpResponseRedirect(reverse('login_view'))
        else:
            form = RegistrationForm
            return render(request, 'register.html', {'form': form})
