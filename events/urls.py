from django.urls import path
from .views import Login, Logout, Signup, home
from . import views
urlpatterns = [
	path('', home, name='home'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create/', views.create_event, name='create-view'),
    path('list/', views.upcoming_list, name='event-list'),
    path('detail/<int:event_id>/', views.event_detail, name='event-detail'),
    path('update/<int:event_id>/', views.update_event, name='update-event'),
    path('book/<int:event_id>/', views.book_event, name='book-event'),
    path('delete/<int:booking_id>/', views.cancel_booking, name='cancel-booking'),
    path('update/profile/', views.update_profile, name='update-profile'),
    path('send/', views.send_email, name='email'),
    path('profile/<str:username>/', views.view_profile, name='view-profile'),
    path('follow/<str:username>/', views.follow, name='follow'),
    # path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
]