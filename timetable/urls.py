from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

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
router.register('studentdata', booking.views.UserViewSet, basename='studentdata')

# Authentication URLs
router.register('session', authentication.views.SessionViewSet, basename='session')
router.register('telegramuser', authentication.views.TelegramUserViewSet, basename='telegramuser')
router.register('telegrambot', authentication.views.TelegramBotViewSet, basename='telegrambot')
router.register('querytoken', authentication.views.TimeLimitedQueryParamTokenViewSet, basename='querytoken')

# Assesment URLs
router.register('question', assessment.views.QuestionViewSet)
router.register('answer', assessment.views.AnswerViewSet, basename='answer')
router.register('choice', assessment.views.ChoiceViewSet, basename='choice')
router.register('export', assessment.views.ExportViewSet, basename='export')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
