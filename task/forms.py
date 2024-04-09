from django import forms
from .models import Task
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

class TaskForm(forms.ModelForm):
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority']
        

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    
    
    def clean_confirm_password(self):
        cd = self.cleaned_data
        if cd['password'] != cd['confirm_password']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['confirm_password']
    
class UserProfileForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class UserPasswordChange(forms.Form):
    current_password = forms.CharField(max_length=100, widget=forms.PasswordInput, label='Enter your current password')
    new_password = forms.CharField(max_length=100, widget=forms.PasswordInput, label='Enter your new password')
    new_confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm your new password')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__( *args, **kwargs)
    
    def clean_new_confirm_password(self):
        cd = self.cleaned_data
        if cd['new_password'] != cd['new_confirm_password']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['new_confirm_password']

    def clean_current_password(self):
        cd = self.cleaned_data
        if not self.user.check_password(cd['current_password']):
            raise forms.ValidationError('Invalid password')
        return cd['current_password']
    

class PasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=150, label='Enter your email address')
    
    def clean_email(self):
        cd = self.cleaned_data
        user = get_object_or_404(User, email=cd['email'])
        if not user:
            raise forms.ValidationError('Invalid email')
        return cd['email']


class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(max_length=150, widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(max_length=150, widget=forms.PasswordInput)
    
    def clean_new_password_confirm(self):
        cd = self.cleaned_data
        if cd['new_password'] != cd['new_password_confirm']:
            raise forms.ValidationError('Invalid password')
        return cd['new_password']