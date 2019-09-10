from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    
)
urlpatterns = [
	path('list/', views.EventsList.as_view(), name="api-list"),
    path('list/<str:owner>/', views.OwnerEventsList.as_view(), name="api-owner-list"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', views.Register.as_view(), name='api-register'),
    path('create/', views.CreateEvent.as_view(), name='api-create'),
    path('update/<int:event_id>/', views.UpdateEvent.as_view(), name='api-update'),
    path('book/<int:event_id>/', views.CreateBooking.as_view(), name='api-book'),
    path('list/bookers/<int:event_id>/', views.BookersList.as_view(), name='api-bookers-list'),
    path('mybookings/', views.MyBookingsList.as_view(), name='api-my-bookings'),
    path('following/', views.FollowingList.as_view(), name='api-following'),
    path('follow/<str:username>/', views.Follow.as_view(), name='api-follow'),
    path('unfollow/<str:username>/', views.Unfollow.as_view(), name='api-unfollow'),


]