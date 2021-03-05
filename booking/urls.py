from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('booking', views.BookingApiViewSet)

urlpatterns = [
    path('user/', views.CreateUserView.as_view(), name='create-user'),
    path('tutor/', views.TutorApiView.as_view(), name='tutor'),
    path('group/', views.GroupApiView.as_view(), name='group'),
    path('module/', views.ModuleApiView.as_view(), name='module'),
    path('room/', views.RoomApiView.as_view(), name='room'),
    path('token/', obtain_auth_token),
    path('timetable-data/', views.TimeTableDataApiView.as_view(), name='timetable-data'),
    path('', include(router.urls)),
]



