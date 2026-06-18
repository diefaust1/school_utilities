from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Question, StudentAnswer, Test, TestSubmission, User


@admin.register(User)
class AutoGraderUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "role", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "length_minutes", "is_active", "created_by")
    list_filter = ("is_active", "date")
    search_fields = ("title",)
    inlines = [QuestionInline]


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ("question", "answer_text")


@admin.register(TestSubmission)
class TestSubmissionAdmin(admin.ModelAdmin):
    list_display = ("test", "student_first_name", "student_last_name", "student", "status", "submitted_at")
    list_filter = ("test", "status", "submitted_at")
    search_fields = ("student_first_name", "student_last_name", "student__email", "test__title")
    inlines = [StudentAnswerInline]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
