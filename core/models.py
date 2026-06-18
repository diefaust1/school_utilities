from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields) -> User:
        if not email:
            raise ValueError("An e-mail address is required.")

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.TEACHER)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("A superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("A superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    if TYPE_CHECKING:
        objects: UserManager
    else:
        objects = UserManager()

    def __str__(self):
        return self.get_full_name() or self.email


class Test(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    length_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_tests",
    )

    class Meta:
        ordering = ("date", "title")

    def __str__(self):
        return self.title

    @property
    def total_points(self):
        return sum(question.points for question in self.questions.all())


class Question(models.Model):
    class AnswerType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"
        FREE_TEXT = "free_text", "Free text"

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=200)
    description = models.TextField()
    answer_type = models.CharField(max_length=20, choices=AnswerType.choices)
    points = models.PositiveIntegerField()
    option_a = models.CharField(max_length=255, blank=True)
    option_b = models.CharField(max_length=255, blank=True)
    option_c = models.CharField(max_length=255, blank=True)
    option_d = models.CharField(max_length=255, blank=True)
    correct_choice = models.CharField(max_length=1, blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.title

    @property
    def options(self):
        return [
            (key, value)
            for key, value in (
                ("A", self.option_a),
                ("B", self.option_b),
                ("C", self.option_c),
                ("D", self.option_d),
            )
            if value
        ]


class TestSubmission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        REOPENED = "reopened", "Reopened"

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="test_submissions",
    )
    student_first_name = models.CharField(max_length=150)
    student_last_name = models.CharField(max_length=150)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )
    reopened_at = models.DateTimeField(blank=True, null=True)
    reopened_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reopened_submissions",
    )

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self):
        return f"{self.student_first_name} {self.student_last_name} - {self.test}"


class StudentAnswer(models.Model):
    submission = models.ForeignKey(
        TestSubmission,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()

    class Meta:
        ordering = ("question_id",)

    def __str__(self):
        return f"Answer to {self.question}"
