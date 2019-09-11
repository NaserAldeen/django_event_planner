from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .utils import send_email
import datetime   


class Event(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    location = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    seats = models.PositiveIntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_events")

    def __str__(self):
        return self.title

    def get_seats_left(self):
        return self.seats - sum(self.bookings.values_list('tickets', flat=True))

    def is_cancelable(self):
        if (datetime.datetime.combine(self.date, self.time) - datetime.datetime.now()).seconds > 3*60*60:
            return True
        else:
            return False
    def did_end(self):
        if datetime.datetime.combine(self.date, self.time) <= datetime.datetime.now():
            return True
        else:
            return False


class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    time = models.DateTimeField(default=timezone.now)
    tickets = models.PositiveIntegerField()

    def __str__(self):
        return self.user.username

    def clean(self):
        if self.tickets > self.event.get_seats_left():
            raise ValidationError('Not enough seats')
        
class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # following = models.ManyToManyField(User, null=True, blank=True, related_name='followers')
    followers = models.ManyToManyField(User, null=True, blank=True, related_name='following')
    def __str__(self):
        return self.user.username

# @receiver(post_save, sender=MyUser)
# def get_followings(instance, *args, **kwargs):
#     if instance.followers.all().last():   
#         MyUser.objects.get(user=instance.followers.all().last()).following.add(instance.user)

@receiver(post_save, sender=Event)
def send_emails(instance,created, *args, **kwargs):
    if created:
        email_body = """
                <h1>{} has created a new event!</h1>
        <p><strong>Title:</strong> {}</p>
        <p><strong>Description:</strong> {}</p>
        <p><strong>Date:</strong> {}</p>
        <p><strong>Time:</strong> {}</p>
        <p><strong>Available Seats:</strong> {}</p>
        """.format(instance.owner.username, instance.title, instance.description,
            instance.date, instance.time, instance.seats)
        
        for emaill in instance.owner.followers.values_list('user__email', flat=True):
            try:
                send_email(emaill, "Announcement!", email_body)
            except :
                pass


