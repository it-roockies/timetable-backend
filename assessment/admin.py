from django.contrib import admin
from .models import Question, Answer, Choice


class AnswerAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "question", "answer")
    list_filter = ("user", "question", "teacher", "subject")
    readonly_fields = ("user", "question", "teacher", "subject", "answer", "date")

    def has_add_permission(self, request):
        return False


class AnswerInline(admin.TabularInline):
    model = Answer
    can_delete = False
    readonly_fields = ("user", "question", "teacher", "subject", "answer")

    def has_add_permission(self, request, obj):
        return False

class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Choice)
