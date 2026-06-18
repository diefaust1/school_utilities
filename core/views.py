from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AccountInfoForm,
    RegistrationForm,
    TestActivationForm,
    TestSubmissionForm,
)
from .models import Test, TestSubmission, User


def teacher_required(user):
    return user.role == User.Role.TEACHER


def login_page(request):
    if request.user.is_authenticated:
        return redirect("test-overview")

    error = None
    email = ""
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("test-overview")

        error = "The e-mail address or password is incorrect."

    return render(request, "core/login.html", {"error": error, "email": email})


def registration_page(request):
    if request.user.is_authenticated:
        return redirect("test-overview")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("test-overview")

    return render(request, "core/registration.html", {"form": form})


@login_required
def test_overview(request):
    tests = Test.objects.prefetch_related("questions").all()
    submitted_test_ids = set(
        TestSubmission.objects.filter(
            student=request.user,
            status=TestSubmission.Status.SUBMITTED,
        ).values_list("test_id", flat=True)
    )

    return render(
        request,
        "core/test_overview.html",
        {
            "active_page": "overview",
            "submitted_test_ids": submitted_test_ids,
            "tests": tests,
        },
    )


@login_required
def toggle_test_activation(request, test_id):
    if not teacher_required(request.user):
        return HttpResponseForbidden("Only teacher accounts can change test status.")
    if request.method != "POST":
        return redirect("test-overview")

    test = get_object_or_404(Test, pk=test_id)
    form = TestActivationForm(request.POST, instance=test)
    if form.is_valid():
        form.save()

    return redirect("test-overview")


@login_required
def test_detail(request, test_id):
    test = get_object_or_404(Test.objects.prefetch_related("questions"), pk=test_id)
    existing_submission = TestSubmission.objects.filter(
        test=test,
        student=request.user,
        status=TestSubmission.Status.SUBMITTED,
    ).prefetch_related("answers").first()
    latest_submission = (
        TestSubmission.objects.filter(test=test, student=request.user)
        .prefetch_related("answers")
        .first()
    )
    can_take_test = test.is_active and existing_submission is None
    form = TestSubmissionForm(
        request.POST or None,
        test=test,
        user=request.user,
        disabled=not can_take_test,
        initial_submission=existing_submission or latest_submission,
    )
    submitted = request.GET.get("submitted") == "1"

    if request.method == "POST" and not can_take_test:
        return HttpResponseForbidden("This test is not currently available.")

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"{request.path}?submitted=1")

    return render(
        request,
        "core/test_detail.html",
        {
            "active_page": "overview",
            "form": form,
            "can_take_test": can_take_test,
            "display_submission": existing_submission or latest_submission,
            "existing_submission": existing_submission,
            "question_fields": [
                (question, form[form.answer_field_name(question)])
                for question in form.questions
            ],
            "submitted": submitted,
            "test": test,
        },
    )


@login_required
def test_creation(request):
    if not teacher_required(request.user):
        return HttpResponseForbidden("Only teacher accounts can access test creation.")

    return render(
        request,
        "core/test_creation.html",
        {"active_page": "creation"},
    )


@login_required
def test_submissions(request):
    if not teacher_required(request.user):
        return HttpResponseForbidden("Only teacher accounts can view submissions.")

    tests = (
        Test.objects.prefetch_related(
            "questions",
            "submissions__student",
            "submissions__answers__question",
        )
        .all()
    )

    return render(
        request,
        "core/test_submissions.html",
        {"active_page": "submissions", "tests": tests},
    )


@login_required
def reopen_submission(request, submission_id):
    if not teacher_required(request.user):
        return HttpResponseForbidden("Only teacher accounts can reopen submissions.")
    if request.method != "POST":
        return redirect("test-submissions")

    submission = get_object_or_404(TestSubmission, pk=submission_id)
    submission.status = TestSubmission.Status.REOPENED
    submission.reopened_at = timezone.now()
    submission.reopened_by = request.user
    submission.save(update_fields=("status", "reopened_at", "reopened_by"))

    return redirect("test-submissions")


@login_required
def account_info(request):
    form = AccountInfoForm(request.POST or None, instance=request.user)
    saved = request.GET.get("saved") == "1"

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"{request.path}?saved=1")

    return render(
        request,
        "core/account_info.html",
        {"active_page": "account", "form": form, "saved": saved},
    )


def logout_page(request):
    if request.method == "POST":
        logout(request)
    return redirect("login")
