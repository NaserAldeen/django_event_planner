from rest_framework import serializers
from django.contrib.auth.models import User
from events.models import Booking, Event, MyUser

class MyBookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
class FollowSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    class Meta:
        model = MyUser
        fields = ['username']

    def get_username(self, obj):
        return obj.user.username
    
class EventListSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = '__all__'

    def get_owner(self, obj):
        return obj.owner.username

class BookersListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['user', 'tickets']
    def get_user(self, obj):
        return obj.user.username

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

  