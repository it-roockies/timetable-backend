from django.contrib import admin
from . import models


class TeacherAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "short")
    readonly_fields = ("teacher_id",)


class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name",)
    readonly_fields = ("classroom_id",)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "short")
    readonly_fields = ("subject_id",)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    readonly_fields = ("group_id",)


class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "teacher_list", "group_list")
    readonly_fields = ("lesson_id",)

    @admin.display(description="Teachers")
    def teacher_list(self, obj):
        teachers = [str(t) for t in obj.teachers.all()]
        return ", ".join(teachers)

    @admin.display(description="Groups")
    def group_list(self, obj):
        groups = [str(g) for g in obj.groups.all()]
        return ", ".join(groups)

class MessageAdmin(admin.ModelAdmin):
    list_display = ("message_id", "text")
    readonly_fields = ("message_id",)

admin.site.register(models.User)
admin.site.register(models.Booking)
admin.site.register(models.Subject, SubjectAdmin)
admin.site.register(models.Classroom, ClassroomAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Teacher, TeacherAdmin)
admin.site.register(models.Lesson, LessonAdmin)
admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.TeacherSubject)
admin.site.register(models.Event)
admin.site.register(models.EventMember)
