from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('booking', views.BookingViewSet)
router.register('timetable', views.TimeTableViewSet, basename='timetable')

urlpatterns = [
    path('user/', views.CreateUserView.as_view(), name='create-user'),
    path('user/<int:user_id>', views.UserDetailView.as_view(), name='user-detail'),
    path('teacher/', views.TeacherApiView.as_view(), name='teacher'),
    path('group/', views.GroupApiView.as_view(), name='group'),
    path('subject/', views.SubjectApiView.as_view(), name='subject'),
    path('classroom/', views.ClassroomApiView.as_view(), name='classroom'),
    path('token/', obtain_auth_token),
    path('', include(router.urls)),
]



