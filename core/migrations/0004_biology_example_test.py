import datetime

from django.db import migrations


def create_biology_test(apps, schema_editor):
    test_model = apps.get_model("core", "Test")
    question_model = apps.get_model("core", "Question")

    biology_test, _ = test_model.objects.get_or_create(
        title="Biology - Cell Structure",
        defaults={
            "date": datetime.date(2026, 6, 23),
            "length_minutes": 60,
            "is_active": True,
            "instructions": "Answer all biology questions. Multiple-choice questions have one correct answer.",
        },
    )

    questions = [
        {
            "title": "Cell Organelle",
            "description": "Which organelle is mainly responsible for producing energy in animal cells?",
            "answer_type": "multiple_choice",
            "points": 4,
            "option_a": "Nucleus",
            "option_b": "Mitochondrion",
            "option_c": "Ribosome",
            "option_d": "Cell membrane",
            "correct_choice": "B",
        },
        {
            "title": "Plant Cells",
            "description": "Which structure is found in plant cells but not in animal cells?",
            "answer_type": "multiple_choice",
            "points": 4,
            "option_a": "Cell wall",
            "option_b": "Cytoplasm",
            "option_c": "Nucleus",
            "option_d": "Mitochondrion",
            "correct_choice": "A",
        },
        {
            "title": "Explain Cell Membranes",
            "description": "Explain the function of the cell membrane in your own words.",
            "answer_type": "free_text",
            "points": 6,
        },
    ]

    for question in questions:
        question_model.objects.get_or_create(
            test=biology_test,
            title=question["title"],
            defaults=question,
        )


def remove_biology_test(apps, schema_editor):
    test_model = apps.get_model("core", "Test")
    test_model.objects.filter(title="Biology - Cell Structure").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_submission_status"),
    ]

    operations = [
        migrations.RunPython(create_biology_test, remove_biology_test),
    ]
