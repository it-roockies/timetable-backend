from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

import assessment.views
import authentication.views
import booking.views

router = DefaultRouter()

# Booking URLs
router.register('booking', booking.views.BookingViewSet)
router.register('teacher', booking.views.TeacherViewSet)
router.register('group', booking.views.GroupViewSet)
router.register('subject', booking.views.SubjectViewSet)
router.register('classroom', booking.views.ClassroomViewSet)
router.register('timetable', booking.views.TimeTableViewSet, basename='timetable')
router.register('telegramuser', authentication.views.TelegramUserViewSet, basename='telegramuser')
router.register('telegrambot', authentication.views.TelegramBotViewSet, basename='telegrambot')
router.register('studentdata', booking.views.UserViewSet, basename='student-data')


# Assesment URLs
router.register('question', assessment.views.QuestionViewSet)
router.register('answer', assessment.views.AnswerViewSet, basename='answer')
router.register('choice', assessment.views.ChoiceViewSet, basename='choice')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', obtain_auth_token),
    path('api/csv/', assessment.views.csv_file)
]
