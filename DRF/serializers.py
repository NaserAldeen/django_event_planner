from rest_framework import serializers
from django.contrib.auth.models import User
from events.models import Booking, Event, MyUser

class MyBookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class BookersListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
     )
    class Meta:
        model = Booking
        fields = ['user', 'tickets']

class EventListSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
     )
    bookers = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id', 'owner', 'title', 'description', 'location', 'date', 'time', 'seats', 'bookers']
    def get_bookers(self, obj):
        return BookersListSerializer(Booking.objects.filter(event=obj), many=True).data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password',]

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        new_user = User(username=username)
        new_user.set_password(password)
        new_user.save()
        MyUser.objects.create(user=new_user)
        return validated_data
class FollowingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['user',]
    def get_user(self, obj):
        return obj.user.username

class CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        exclude = ['owner',]

class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        exclude = ['event', 'user']

class ProfileSerializer(serializers.ModelSerializer):
    events = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    bookings = serializers.SerializerMethodField()
    class Meta:
        model = MyUser
        fields = ['events', 'followers', 'bookings']
    def get_events(self, obj):
        print(obj)
        return EventListSerializer(Event.objects.filter(owner=obj.user), many=True).data

    def get_followers(self, obj):
        return len(obj.followers.all())

    def get_bookings(self, obj):
        return MyBookingsSerializer(Booking.objects.filter(user=obj.user), many=True).data

