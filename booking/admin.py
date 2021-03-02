from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Booking)
admin.site.register(models.Module)
admin.site.register(models.Room)
admin.site.register(models.Group)
admin.site.register(models.Tutor)
