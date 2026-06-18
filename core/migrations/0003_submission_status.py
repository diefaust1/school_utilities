import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_tests_and_submissions"),
    ]

    operations = [
        migrations.AddField(
            model_name="testsubmission",
            name="status",
            field=models.CharField(
                choices=[("submitted", "Submitted"), ("reopened", "Reopened")],
                default="submitted",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="testsubmission",
            name="reopened_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="testsubmission",
            name="reopened_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reopened_submissions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
