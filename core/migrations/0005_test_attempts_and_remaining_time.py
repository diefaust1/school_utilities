import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_biology_example_test"),
    ]

    operations = [
        migrations.AddField(
            model_name="testsubmission",
            name="reopen_duration_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="testsubmission",
            name="remaining_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="TestAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("duration_seconds", models.PositiveIntegerField()),
                ("student_first_name", models.CharField(blank=True, max_length=150)),
                ("student_last_name", models.CharField(blank=True, max_length=150)),
                (
                    "status",
                    models.CharField(
                        choices=[("in_progress", "In progress"), ("submitted", "Submitted")],
                        default="in_progress",
                        max_length=20,
                    ),
                ),
                (
                    "source_submission",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reopened_attempts",
                        to="core.testsubmission",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="test_attempts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submitted_submission",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="source_attempt",
                        to="core.testsubmission",
                    ),
                ),
                (
                    "test",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attempts",
                        to="core.test",
                    ),
                ),
            ],
            options={
                "ordering": ("-started_at",),
            },
        ),
        migrations.CreateModel(
            name="TestAttemptAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer_text", models.TextField(blank=True)),
                (
                    "attempt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="core.testattempt",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.question"),
                ),
            ],
            options={
                "ordering": ("question_id",),
            },
        ),
        migrations.AddConstraint(
            model_name="testattemptanswer",
            constraint=models.UniqueConstraint(
                fields=("attempt", "question"),
                name="unique_attempt_answer_question",
            ),
        ),
    ]
