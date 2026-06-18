import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_example_test(apps, schema_editor):
    test_model = apps.get_model("core", "Test")
    question_model = apps.get_model("core", "Question")

    example_test, _ = test_model.objects.get_or_create(
        title="Mathematics - Basics",
        defaults={
            "date": datetime.date(2026, 6, 18),
            "length_minutes": 45,
            "is_active": True,
            "instructions": "Answer all questions. Multiple-choice questions have one correct answer.",
        },
    )

    questions = [
        {
            "title": "Linear Equation",
            "description": "What is x in the equation 3x + 7 = 22?",
            "answer_type": "multiple_choice",
            "points": 4,
            "option_a": "3",
            "option_b": "5",
            "option_c": "7",
            "option_d": "15",
            "correct_choice": "B",
        },
        {
            "title": "Geometry",
            "description": "A rectangle has a length of 8 cm and a width of 3 cm. What is its area?",
            "answer_type": "multiple_choice",
            "points": 4,
            "option_a": "11 cm2",
            "option_b": "16 cm2",
            "option_c": "24 cm2",
            "option_d": "64 cm2",
            "correct_choice": "C",
        },
        {
            "title": "Explain Your Method",
            "description": "Explain how you can check whether your answer to an equation is correct.",
            "answer_type": "free_text",
            "points": 6,
        },
    ]

    for question in questions:
        question_model.objects.get_or_create(
            test=example_test,
            title=question["title"],
            defaults=question,
        )


def remove_example_test(apps, schema_editor):
    test_model = apps.get_model("core", "Test")
    test_model.objects.filter(title="Mathematics - Basics").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Test",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("date", models.DateField()),
                ("length_minutes", models.PositiveIntegerField()),
                ("is_active", models.BooleanField(default=True)),
                ("instructions", models.TextField(blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_tests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("date", "title"),
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                (
                    "answer_type",
                    models.CharField(
                        choices=[("multiple_choice", "Multiple choice"), ("free_text", "Free text")],
                        max_length=20,
                    ),
                ),
                ("points", models.PositiveIntegerField()),
                ("option_a", models.CharField(blank=True, max_length=255)),
                ("option_b", models.CharField(blank=True, max_length=255)),
                ("option_c", models.CharField(blank=True, max_length=255)),
                ("option_d", models.CharField(blank=True, max_length=255)),
                ("correct_choice", models.CharField(blank=True, max_length=1)),
                (
                    "test",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="core.test"),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="TestSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("student_first_name", models.CharField(max_length=150)),
                ("student_last_name", models.CharField(max_length=150)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="test_submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "test",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="core.test"),
                ),
            ],
            options={
                "ordering": ("-submitted_at",),
            },
        ),
        migrations.CreateModel(
            name="StudentAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer_text", models.TextField()),
                (
                    "question",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.question"),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="core.testsubmission",
                    ),
                ),
            ],
            options={
                "ordering": ("question_id",),
            },
        ),
        migrations.RunPython(create_example_test, remove_example_test),
    ]
