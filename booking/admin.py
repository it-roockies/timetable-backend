from django.contrib import admin
from . import models
# Register your models here.

class TutorAdmin(admin.ModelAdmin):
    readonly_fields = ('teacher_id',)


admin.site.register(models.User)
admin.site.register(models.Booking)
admin.site.register(models.Subject)
admin.site.register(models.Classroom)
admin.site.register(models.Group)
admin.site.register(models.Teacher, TutorAdmin)
