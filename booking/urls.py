from django.urls import path
from . import views


urlpatterns = [
    path('user/', views.CreateUserView.as_view(), name='create-user'),
    path('booking/', views.BookingApiView.as_view(), name='booking'),
    path('tutor/', views.TutorApiView.as_view(), name='tutor'),
    path('group/', views.GroupApiView.as_view(), name='group'),
    path('module/', views.ModuleApiView.as_view(), name='module'),
    path('room/', views.RoomApiView.as_view(), name='room')
]

