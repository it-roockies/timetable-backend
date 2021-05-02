from django.contrib import admin
from . import models


class TeacherAdmin(admin.ModelAdmin):
    readonly_fields = ("teacher_id",)


class ClassroomAdmin(admin.ModelAdmin):
    readonly_fields = ("classroom_id",)


class SubjectAdmin(admin.ModelAdmin):
    readonly_fields = ("subject_id",)


class GroupAdmin(admin.ModelAdmin):
    readonly_fields = ("group_id",)


class LessonAdmin(admin.ModelAdmin):
    readonly_fields = ("lesson_id",)


admin.site.register(models.User)
admin.site.register(models.Booking)
admin.site.register(models.Subject, SubjectAdmin)
admin.site.register(models.Classroom, ClassroomAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Teacher, TeacherAdmin)
admin.site.register(models.Lesson, LessonAdmin)
admin.site.register(models.Message)
admin.site.register(models.TeacherSubject)
admin.site.register(models.Event)
admin.site.register(models.EventMember)
