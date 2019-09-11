from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, DestroyAPIView, CreateAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from events.models import Booking, Event, MyUser
from django.utils import timezone
from .serializers import EventListSerializer, ProfileSerializer, RegisterSerializer, CreateSerializer, CreateBookingSerializer, BookersListSerializer, MyBookingsSerializer, FollowingSerializer
from .permissions import IsOwner, CanBook, IsValidNumber
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.

class EventsList(ListAPIView):
    queryset = Event.objects.filter(date__gte=timezone.now())
    serializer_class = EventListSerializer
    
class OwnerEventsList(ListAPIView):
    serializer_class = EventListSerializer

    def get_queryset(self):
        return Event.objects.filter(owner__username=self.kwargs['owner'])

class Register(CreateAPIView):
    serializer_class = RegisterSerializer

class CreateEvent(CreateAPIView):
    serializer_class = CreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UpdateEvent(RetrieveUpdateAPIView):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated, IsOwner, ]
    serializer_class = CreateSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'event_id'

class CreateBooking(CreateAPIView):
    serializer_class = CreateBookingSerializer
    permission_classes = [IsAuthenticated, IsValidNumber, CanBook, ]
    def perform_create(self, serializer):

        serializer.save(event=Event.objects.get(id=self.kwargs['event_id']), user=self.request.user)

class Follow(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request, username):
    
        obj = MyUser.objects.get(user__username=username)
        if obj in request.user.following.all():
            obj.followers.remove(request.user)
            return Response("Unfollowed") 
        else:
            obj.followers.add(request.user)
            return Response("Followed")        


class BookersList(ListAPIView):
    serializer_class = BookersListSerializer
    permission_classes = [IsAuthenticated, IsOwner, ]
    def get_queryset(self):
        event = Event.objects.get(id=self.kwargs['event_id'])
        return event.bookings.all()

class FollowingList(ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated,]
    def get_queryset(self):
        return self.request.user.following.all()

class MyBookingsList(ListAPIView):
    serializer_class = MyBookingsSerializer
    permission_classes = [IsAuthenticated,]
    
    def get_queryset(self):
        return self.request.user.bookings.all()

class ProfilePage(ListAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return MyUser.objects.filter(user__username=self.kwargs['username'])

