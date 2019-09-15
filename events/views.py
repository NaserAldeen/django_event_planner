from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View
from .forms import UserSignup, UserLogin, EventCreateForm,UserUpdate
from django.contrib import messages
from django.utils import timezone
from .models import Event, Booking, MyUser
from django.db.models import Q
from datetime import datetime, date
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.paginator import Paginator
from .utils import send_email
        

def home(request):
    event_list=Event.objects.filter(date__gte=timezone.now()).order_by("date","time")

    context = {
    'upcoming_events':event_list[:6],
    
    }
    return render(request, 'home.html', context)

class Signup(View):
    form_class = UserSignup
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            MyUser.objects.create(user=user,)   
            messages.success(request, "You have successfully signed up.")
            login(request, user)
            return redirect("home")
        messages.warning(request, form.errors)
        return redirect("signup")


class Login(View):
    form_class = UserLogin
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
           return redirect("home")
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, "Welcome Back!")
                return redirect('dashboard')
            messages.warning(request, "Wrong email/password combination. Please try again.")
            return redirect("login")
        messages.warning(request, form.errors)
        return redirect("login")


class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect("login")


def dashboard_view(request):
    if request.user.is_anonymous:
        return redirect("login")

    context = {
        'my_events': request.user.my_events.all(),
        'attended': request.user.bookings.all(),
       
    }
    return render(request, 'dashboard.html', context)

def create_event(request):

    if request.user.is_anonymous:
        messages.success(request, "You need to login first")
        return redirect("login")
    form = EventCreateForm()
    if request.method == "POST":
        form = EventCreateForm(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            temp.owner = request.user
            temp.tags = temp.listify()
            temp.save()

            return redirect("dashboard")
    context = {
        "form":form
    }
    return render(request, 'create_event.html', context)

def upcoming_list(request):

    if request.user.is_anonymous:
        messages.success(request, "You need to log-in first")
        return redirect("login")

    events = Event.objects.filter(date__gte=timezone.now()).order_by("date","time")

    query = request.GET.get("q")
    query_len = 0
    if query:
        query=query.strip()
        events = Event.objects.filter(
            Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(owner__username__icontains=query)|
            Q(tags__icontains=query)
         

            ).distinct().order_by("date","time")
        query_len = len(events)

    p = Paginator(events, 6)
    number = int(request.GET.get("page_number", 1))
    events = p.page(number)
    
    context = {
        'upcoming_events': events,
        'number_of_pages': range(1, p.num_pages+1),
        'query_len': query_len
    }
    return render(request, 'list.html', context)

def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    qr = "Event title: "+event.title + "\n" + "Event Organizer: " + event.owner.username + "\n"+ "Event date: " + str(event.date) + "\n"+ "Event time: " + str(event.time)
    context = {
        "event": event,
        'bookers': event.bookings.all(),
        "qr":qr
       
    }
    return render(request, "detail.html", context)

def update_event(request, event_id):

    obj = Event.objects.get(id=event_id)
    obj.tags = obj.unlistify()
    if not request.user == obj.owner:
        return redirect('home')

    form = EventCreateForm(instance=obj)
    if request.method == "POST":
        form = EventCreateForm(request.POST, instance=obj)
        if form.is_valid():
            tem = form.save(commit=False)
            tem.tags = tem.listify()
            tem.save()
            return redirect("event-detail", obj.id)

    context = {
        "event":obj,
        "form":form
    }
    return render(request, 'update.html', context)

def book_event(request, event_id):
    if request.user.is_anonymous:
        return redirect('login')

    obj = Event.objects.get(id=event_id)
    if datetime.combine(obj.date, obj.time) < datetime.now():
        messages.warning(request, "This is an old event. You cannot book it")
        return redirect('event-detail', obj.id)
    number = int(request.GET.get("num"))
    if number > obj.get_seats_left():
        messages.warning(request, "Not enough tickets to book")
        return redirect('event-detail', obj.id )
    if number <= 0:
        messages.warning(request, "Please enter a valid number")
        return redirect('event-detail', obj.id )

    booking_obj = Booking.objects.create(user=request.user, event= obj, tickets=number, time=timezone.now())
    email_body = """
    <h1>Your booking receipt</h1>
    <p><strong>Event:</strong> {}</p>
    <p><strong>Time:</strong> {}</p>
    <p><strong>Tickets booked:</strong> {}</p>
    <br>
    <p>Thank you!</p>
    """.format(booking_obj.event.title, booking_obj.time, number)
    if not booking_obj.event.owner == request.user:
        try:
            send_email(request.user.email, "Booking Receipt", email_body )
        except:
            pass
    return redirect('event-detail', obj.id )

def cancel_booking(request, booking_id):

    if request.user.is_anonymous:
        messages.warning(request, "You don't own this booking. Please log-in")
        return redirect('login' )
    obj = Booking.objects.get(id=booking_id)

    if not request.user == obj.user:
        messages.warning(request, "You don't own this booking.")
        return redirect('home')
    obj.delete()

    return redirect("dashboard")

def update_profile(request):

    if request.user.is_anonymous:
        messages.warning(request, "You need to log-in first in order to update your profile.")
        return redirect("login")
    form = UserUpdate(instance=request.user)
    if request.method == "POST":
        form = UserUpdate(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    context = {
        "form":form
    }
    return render(request, 'update_profile.html', context)
    
def view_profile(request, username):
    button_text = ''
    if MyUser.objects.get(user__username=username) not in request.user.following.all():
        button_text = 'Follow'
    else: button_text = 'Unfollow'
    if request.user.username == username:
        button_text = 'no'
    context = {
        "events": Event.objects.filter(owner__username=username),
        'organizer': username,
        'followers_count': len(MyUser.objects.get(user__username=username).followers.all()),
        'button_text': button_text
    }
    return render(request, "profile.html", context)


def follow(request, username):
    print(request.user.following.all())
    if request.user.is_anonymous:
        messages.warning(request, "You need to log-in in order to follow this organizer")
        return redirect("login")
    
    obj = MyUser.objects.get(user__username=username)
    if obj in request.user.following.all():
        obj.followers.remove(request.user) 
    else:
        obj.followers.add(request.user)
    
    return redirect("view-profile", username)
