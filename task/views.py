from django.shortcuts import render
from .models import Task
from .forms import TaskForm, LoginForm, RegistrationForm, UserProfileForm, UserPasswordChange, PasswordResetForm, PasswordResetConfirmForm
from django.utils.text import slugify
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes


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
                author = request.user,
                priority = cd['priority']
            )
            new_task.save()
        return HttpResponseRedirect(reverse('task_list'))
                    
    elif request.method == 'GET':
        form = TaskForm
        return render(request, 'task_create.html', {'form': form})


@login_required
def task_update(request, pk, status=None):           
    task = get_object_or_404(Task, id=pk)
    if request.method == 'POST':
        form  = TaskForm(request.POST, instance=task)
        if status:
            if status == 'W':
                task.status = Task.Status.STARTED
                task.save()
            elif status == 'S':
                task.status = Task.Status.COMPLITED
                task.save()
            else:
                task.status = Task.Status.WAITING
                task.save()
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
    print(request.POST)
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
                    messages.error(request, 'Invalid data ')
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

@login_required
def account(request, pk):
    user = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        user_profile_form = UserProfileForm(instance=user)
        return render(request, 'account.html', {'user_profile_form': user_profile_form})
    
@login_required
def settings(request):
    return render(request, 'settings.html', {})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = UserPasswordChange(request.POST, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.get(id=request.user.id)
            user.set_password(cd['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password hase been changed')
            return HttpResponseRedirect(reverse('task_list'))
        else:
            messages.error(request, 'Invalid password')
            return HttpResponseRedirect(reverse('password_change'))
    elif request.method == 'GET':
        form = UserPasswordChange
        return render(request, 'password_change.html', {'form': form})
    
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.get(email=cd['email'])
            current_path = request.path
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)
            host = request.get_host()
            #url = reverse('', args=[uidb64, token])
            url_parts = (host, current_path[1:-1], uidb64, token)
            url = '/'.join(url_parts)
            message=f'Tape to link and type your new password: {url}'
            send_mail(
                f"Reset your password",
                message,
                'mr.eduard.zabrodskiy@gmail.com',
                [cd['email']]   
            )
            return HttpResponseRedirect(reverse('login_view'))
    elif request.method == 'GET':
        form = PasswordResetForm
        return render(request, 'password_reset.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    user_id = urlsafe_base64_decode(uidb64).decode()
    user = User.objects.get(id = user_id)
    token = default_token_generator.check_token(user, token)
    if request.method == 'POST':
        print(request.POST)
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user.set_password(cd['new_password'])
            user.save()
            return render(request, 'password_reset_confirm_done.html', {})
    elif request.method == 'GET':
        if user and token:
            form = PasswordResetConfirmForm
            return render(request, 'password_reset_confirm.html', {'form': form})
    #ui = urlsafe_base64_decode(uidb64).decode()