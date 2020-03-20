from django.urls import path
from . import views
from .views import RideCreateView, RideListView, RideDeleteView, RideDetailView, RideUpdateView, Sharer_CreateView, \
    RideSharerUpdateView, RideSharerDeleteView, DriverRegisterView, DriverMenuView, DriverProfileView, DriverDetailView, \
    DriverCompleteView, DriverUpdateView, CompletedRideListView, OwnerUpdateNumberView

urlpatterns = [
    path('about/', views.about, name='ride-about'),
    path('register/', views.register, name='ride-register'),
    path('home/', views.userhome, name = 'user-home'),
    path('home/new/', RideCreateView.as_view(), name = 'ride-req'),
    path('home/sharer/',Sharer_CreateView, name = 'ride-share' ),
    path('home/activities/', RideListView.as_view(), name = 'active-rides'),
    path('home/activities/<int:pk>/delete/', RideDeleteView.as_view(), name = 'ride-delete'),
    path('home/activities/<int:pk>', RideDetailView.as_view(), name = 'ride-detail'),
    path('home/activities/<int:pk>/update/', RideUpdateView.as_view(), name = 'ride-update'),
    path('home/activities/<int:ride_pk>/sharerupdate/<int:sharer_pk>', RideSharerUpdateView, name = 'sharer-update'),
    path('home/activities/<int:ride_pk>/sharerdelete/<int:sharer_pk>', RideSharerDeleteView, name = 'sharer-delete'),
    path('home/driver/register', DriverRegisterView.as_view(), name = 'driver-register'),
    path('home/drivermenu/', DriverMenuView, name = "driver-menu"),
    path('home/drivermenu/profile/<int:pk>', DriverProfileView, name = 'driver-profile'),
    path('home/activities/driver/<int:pk>', DriverDetailView, name='driver-detail'),
    path('home/activities/driver/<int:pk>/complete/', DriverCompleteView, name='driver-complete'),
    path('home/drivermenu/profile/driverupdate/<int:pk>', DriverUpdateView, name='driver-update'),
    path('home/history', CompletedRideListView.as_view(), name="ride-history"),
    path('home/activities/<int:pk>/update_can_shared/', OwnerUpdateNumberView, name='owner-update-no'),
]