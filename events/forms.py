from django import forms
from django.contrib.auth.models import User
from .models import Event

class UserSignup(forms.ModelForm):
    email = forms.CharField(max_length=75, required=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email' ,'password']

        widgets={
        'password': forms.PasswordInput(),
        }


class UserUpdate(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email' ]

  

class UserLogin(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['owner', ]

        widgets={
        'date': forms.DateInput(attrs={'type':'date'}),
        'time': forms.TimeInput(attrs={'type':'time'})
        }