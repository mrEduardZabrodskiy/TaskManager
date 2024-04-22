from django.shortcuts import render
from .models import Task, Notification, UserProfile
from .forms import TaskForm, LoginForm, RegistrationForm, UserForm, UserProfileForm, UserPasswordChange, PasswordResetForm, PasswordResetConfirmForm, EmailChangeForm, UploadFileForm
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
import os


# Create your views here.

@login_required
def task_list(request, sort=None):
    tasks = Task.objects.filter(author=request.user)
    notifications = Notification.objects.filter(user=request.user)
    if request.method == 'POST':
        if request.POST.get('status', False):
            status_filter = request.POST.get('status', False)
            print(status_filter)
            tasks = tasks.filter(status=status_filter)
        if request.POST.get('priority', False):
            priority_filter = request.POST.get('priority', False)
            tasks = tasks.filter(priority=priority_filter)
        if request.POST.get('date', False):
            date = request.POST.getlist('date')
            tasks = tasks.filter(created__range=date)
        if request.POST.get('search', False):
            search = request.POST.get('search', False)
            tasks = tasks.filter(title__contains=search)
        return render(request, 'task_list.html', {'tasks': tasks, 'notifications': notifications, 'notifications_count': notifications.count()})
    elif request.method == 'GET':
        if sort:
            tasks = Task.objects.filter(author=request.user).order_by(sort)
        return render(request, 'task_list.html', {'tasks': tasks, 'notifications': notifications, 'notifications_count': notifications.count()})



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
def task_update(request, pk, status=None, priority=None):
    task = get_object_or_404(Task, id=pk)
    if request.method == 'POST':
        form  = TaskForm(request.POST, instance=task)
        if status != 'None':
            print('STATUS')
            if status == '1W':
                task.status = Task.Status.STARTED
                task.save()
            elif status == '2S':
                task.status = Task.Status.COMPLITED
                task.save()
            else:
                task.status = Task.Status.WAITING
                task.save()
        if priority != 'None':
            print('PRIORITY')
            if priority == '1L':
                task.priority = Task.Priority.MEDIUM
                task.save()
            elif priority == '2M':
                task.priority = Task.Priority.HIGH
                task.save()
            elif priority == '3H':
                task.priority = Task.Priority.LOW
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
            print(form)
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
                UserProfile.objects.create(user=user)
                Notification.objects.create(user=user, title='Confirm your email', url='http://127.0.0.1:8000/settings/')
                messages.success(request, 'Account has been created')
                return HttpResponseRedirect(reverse('login_view'))
        else:
            form = RegistrationForm
            return render(request, 'register.html', {'form': form})



@login_required
def account(request):
    user = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        if 'username' in request.POST:
            form = UserForm(request.POST, instance=user)
            if form.is_valid():
                cd = form.cleaned_data
                user.username = cd['username']
                user.first_name = cd['first_name']
                user.last_name = cd['last_name']
                user.save()
                messages.success(request, 'Account has been updated')
                return HttpResponseRedirect(reverse('account'))
            else:
                messages.error(request, 'Username already in use')
        elif 'image' in request.FILES:
            form = UserProfileForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                cd = form.cleaned_data
                user_profile = UserProfile.objects.get(user=user)
                print(user_profile.image.url)
                if user_profile.image and user_profile.image.url != '/media/users_images/user.png':
                    os.remove((os.path.join('MEDIA_ROOT', user_profile.image.path)))
                user_profile.image = request.FILES['image']
                user_profile.save()
                messages.success(request, 'Photo has been set')
        return HttpResponseRedirect(reverse('account'))
    elif request.method == 'GET':
        user = get_object_or_404(User, id=request.user.id)
        user_form = UserForm(instance=user)
        profile = get_object_or_404(UserProfile, user=user)
        profile_form = UserProfileForm(instance=profile)
        user_image = UserProfile.objects.get(user=request.user)
        notifications = Notification.objects.filter(user=request.user)
        return render(request, 'account.html', {'user_form': user_form, 'profile_form': profile_form, 'user_image': user_image, 'notifications': notifications, 'notifications_count': notifications.count()})



@login_required
def settings(request):
    if request.method == 'POST':
        password_form =UserPasswordChange(request.POST, user=request.user)
        email_form = EmailChangeForm(request.POST, user=request.user)
        user = request.user
        if 'current_password' in request.POST:
            errors = password_form.errors.as_data()
            if password_form.is_valid():
                cd_password = password_form.cleaned_data
                user.set_password(cd_password['new_confirm_password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password has been set')
                return HttpResponseRedirect(reverse('settings'))
            else:
                if 'current_password' in errors:
                    messages.error(request, errors['current_password'][0].message)
                elif 'new_confirm_password' in errors:
                    messages.error(request, errors['new_confirm_password'][0].message)
            return HttpResponseRedirect(reverse('settings'))
        elif 'email' in request.POST:
            errors = email_form.errors.as_data()
            if email_form.is_valid():
                cd_email = email_form.cleaned_data  
                user = request.user
                user.email = cd_email['email']
                user.save()
                email_confirm_status = UserProfile.objects.get(user=request.user)
                email_confirm_status.email_confirm_status = False
                email_confirm_status.save()
                if Notification.objects.filter(user = request.user, title='Confirm your email').exists():
                    Notification.objects.filter(user = request.user, title='Confirm your email').delete()
                Notification.objects.create(user=request.user, title='Confirm your email', url='http://127.0.0.1:8000/settings/')
                messages.success(request, 'Email passed')
                return HttpResponseRedirect(reverse('settings'))
            else:
                messages.error(request, errors['email'][0].message)
        elif 'confirm' in request.POST:
            current_path = request.path
            uidb64 = urlsafe_base64_encode(force_bytes(request.user.email))
            token = default_token_generator.make_token(request.user)
            host = request.get_host()
            url_parts = (host, 'email-confirm', uidb64, token)
            url = '/'.join(url_parts)
            message = f'Tape to link and confirm your email: {url}'
            send_mail(
                f'Confirm email',
                message,
                'mr.eduard.zabrodskiy@gmail.com',
                [request.user.email]
            )
            messages.success(request, 'Link was send')
            return HttpResponseRedirect(reverse('settings'))
        return HttpResponseRedirect(reverse('settings'))
    elif request.method == 'GET':
        password_change_form = UserPasswordChange
        email_change_form = EmailChangeForm
        email = UserProfile.objects.get(user=request.user)
        notifications = Notification.objects.filter(user=request.user)
    return render(request, 'settings.html', {
                                                'password_change_form': password_change_form,
                                                'email_change_form': email_change_form,
                                                'email': email.email_confirm_status,
                                                'notifications': notifications,
                                                'notifications_count': notifications.count()})


def email_confirm(request, uidb64, token):
    print(request.GET)
    user_email = urlsafe_base64_decode(uidb64).decode()
    token = default_token_generator.check_token(request.user, token)
    if token and request.user.email == user_email:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.email_confirm_status = True
        user_profile.save()
        notification = Notification.objects.get(user=request.user, title='Confirm your email')
        notification.delete()
        return render(request, 'email_confirm_done.html')
    else:
        messages.error(request, 'Invalid link')
        return HttpResponseRedirect(reverse('settings'))
        


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
            url_parts = (host, current_path[1:-1], uidb64, token)
            url = '/'.join(url_parts)
            message=f'Tape to link and type your new password: {url}'
            send_mail(
                f"Reset password",
                message,
                'mr.eduard.zabrodskiy@gmail.com',
                [cd['email']]   
            )
            return render(request, 'password_reset_done.html', {})
    elif request.method == 'GET':
        form = PasswordResetForm
        return render(request, 'password_reset.html', {'form': form})



def password_reset_confirm(request, uidb64, token):
    user_id = urlsafe_base64_decode(uidb64).decode()
    user = get_object_or_404(User, id=user_id)
    token = default_token_generator.check_token(user, token)
    if request.method == 'POST':
        if user and token:
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user.set_password(cd['new_password'])
                user.save()
                return render(request, 'password_reset_confirm_done.html', {})
            else:
                messages.info(request, 'Somthing wrong')
                return HttpResponseRedirect(reverse('login_view'))
        else:
            messages.error(request,'Invalid link')
            return HttpResponseRedirect(reverse('login_view'))
    elif request.method == 'GET':
        if user and token:
            form = PasswordResetConfirmForm
            return render(request, 'password_reset_confirm.html', {'form': form})
        else:
            messages.error(request, 'Invalid link')
            return HttpResponseRedirect(reverse('login_view'))
        
        


def handler404(request, exception):
    return render(request, 'page_not_found.html', {})