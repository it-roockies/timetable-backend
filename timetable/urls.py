from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

import assessment.views
import authentication.views
import booking.views

router = DefaultRouter()

# Booking URLs
router.register("booking", booking.views.BookingViewSet)
router.register("teacher", booking.views.TeacherViewSet)
router.register("group", booking.views.GroupViewSet)
router.register("subject", booking.views.SubjectViewSet)
router.register("classroom", booking.views.ClassroomViewSet)
router.register("timetable", booking.views.TimeTableViewSet, basename="timetable")
router.register("edupage_import", booking.views.ImportEdupageViewSet, basename="edupage_import")
router.register("studentdata", booking.views.UserViewSet, basename="studentdata")
router.register("grouplesson", booking.views.GroupLessonViewSet, basename="grouplesson")
router.register("message", booking.views.MessageViewSet, basename="message")
router.register("notify", booking.views.NotifyUserViewSet, basename="notify")
router.register("teachersubject", booking.views.TeacherSubjectViewSet, basename="teacher-subject")
router.register("levelsubject", booking.views.LevelSubjectViewSet, basename="level-subject")
router.register("levelteacher", booking.views.LevelTeacherViewSet, basename="level-teacher")
router.register("pystudent", booking.views.PYStudentViewSet, basename="pystudent")
router.register("freeroom", booking.views.AvailableRoomViewSet, basename="free-room")
# Booking room views
router.register("event", booking.views.EventViewSet, basename="event")

# Authentication URLs
router.register('session', authentication.views.SessionViewSet, basename='session')
router.register('telegramuser', authentication.views.TelegramUserViewSet, basename='telegramuser')
router.register('telegrambot', authentication.views.TelegramBotViewSet, basename='telegrambot')
router.register('querytoken', authentication.views.TimeLimitedQueryParamTokenViewSet, basename='querytoken')
router.register('createtotp', authentication.views.TOTPCreateView, basename='create-totp')
router.register('confirmtotp', authentication.views.TOTPConfirmView, basename='create-totp')
router.register('verifytotp', authentication.views.TOTPVerifyView, basename='create-totp')

# Assesment URLs
router.register("question", assessment.views.QuestionViewSet)
router.register("answer", assessment.views.AnswerViewSet, basename="answer")
router.register("choice", assessment.views.ChoiceViewSet, basename="choice")
router.register("export", assessment.views.ExportViewSet, basename="export")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
