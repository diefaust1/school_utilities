from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AccountInfoForm,
    RegistrationForm,
    TestActivationForm,
)
from .models import Test, TestSubmission
from .permissions import can_use_teacher_tools, teacher_action_required
from .submission_attempts import (
    SubmissionAttempt,
    finalize_expired_attempts,
    start_or_continue_attempt,
)
from .teacher_review import load_teacher_review_tests, reopen_submission as reopen_student_submission


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
    if not can_use_teacher_tools(request.user):
        finalize_expired_attempts(student=request.user)

    tests = Test.objects.prefetch_related("questions").all()
    submitted_test_ids = set(
        TestSubmission.objects.filter(
            student=request.user,
            status=TestSubmission.Status.SUBMITTED,
        ).values_list("test_id", flat=True)
    )
    in_progress_test_ids = set(
        request.user.test_attempts.filter(status="in_progress").values_list("test_id", flat=True)
    )

    return render(
        request,
        "core/test_overview.html",
        {
            "active_page": "overview",
            "in_progress_test_ids": in_progress_test_ids,
            "submitted_test_ids": submitted_test_ids,
            "tests": tests,
        },
    )


@login_required
@teacher_action_required("Only teacher accounts can change test status.")
def toggle_test_activation(request, test_id):
    if request.method != "POST":
        return redirect("test-overview")

    test = get_object_or_404(Test, pk=test_id)
    form = TestActivationForm(request.POST, instance=test)
    if form.is_valid():
        form.save()

    return redirect("test-overview")


@login_required
def start_test(request, test_id):
    if can_use_teacher_tools(request.user):
        return redirect("test-detail", test_id=test_id)
    if request.method != "POST":
        return redirect("test-overview")

    test = get_object_or_404(Test, pk=test_id)
    if not test.is_active:
        return HttpResponseForbidden("This test is not currently available.")

    start_or_continue_attempt(test=test, student=request.user)
    return redirect("test-detail", test_id=test.pk)


@login_required
def test_detail(request, test_id):
    test = get_object_or_404(Test.objects.prefetch_related("questions"), pk=test_id)
    attempt = SubmissionAttempt.load(test=test, student=request.user)
    teacher_preview = can_use_teacher_tools(request.user)

    if not teacher_preview and not attempt.has_started and attempt.active_submission is None:
        return redirect("test-overview")

    form = attempt.build_form(
        request.POST or None,
    )
    submitted = request.GET.get("submitted") == "1"

    if request.method == "POST" and (teacher_preview or not attempt.can_submit):
        return HttpResponseForbidden("This test is not currently available.")

    if request.method == "POST" and form.is_valid():
        attempt.submit(form)
        return redirect(f"{request.path}?submitted=1")

    return render(
        request,
        "core/test_detail.html",
        {
            "active_page": "overview",
            "form": form,
            "can_take_test": attempt.can_submit,
            "display_submission": attempt.display_submission,
            "existing_submission": attempt.active_submission,
            "question_fields": attempt.question_fields(form),
            "remaining_seconds": attempt.remaining_seconds,
            "submitted": submitted,
            "test": test,
            "teacher_preview": teacher_preview,
        },
    )


@login_required
def autosave_test_attempt(request, test_id):
    if request.method != "POST" or can_use_teacher_tools(request.user):
        return HttpResponseForbidden("Only active student attempts can be autosaved.")

    test = get_object_or_404(Test.objects.prefetch_related("questions"), pk=test_id)
    attempt = SubmissionAttempt.load(test=test, student=request.user)
    if attempt.active_submission is not None:
        return JsonResponse({"finalized": True, "remaining_seconds": 0})
    if not attempt.can_submit:
        return JsonResponse({"error": "This test has not been started."}, status=400)

    form = attempt.build_form(request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    attempt.save_draft(form)
    attempt = SubmissionAttempt.load(test=test, student=request.user)
    return JsonResponse(
        {
            "finalized": attempt.active_submission is not None,
            "remaining_seconds": attempt.remaining_seconds or 0,
        }
    )


@login_required
@teacher_action_required("Only teacher accounts can access test creation.")
def test_creation(request):
    return render(
        request,
        "core/test_creation.html",
        {"active_page": "creation"},
    )


@login_required
@teacher_action_required("Only teacher accounts can view submissions.")
def test_submissions(request):
    return render(
        request,
        "core/test_submissions.html",
        {"active_page": "submissions", "review_tests": load_teacher_review_tests()},
    )


@login_required
@teacher_action_required("Only teacher accounts can reopen submissions.")
def reopen_submission(request, submission_id):
    if request.method != "POST":
        return redirect("test-submissions")

    submission = get_object_or_404(TestSubmission, pk=submission_id)
    reopen_minutes = request.POST.get("reopen_minutes", "5")
    reopen_student_submission(
        submission=submission,
        teacher=request.user,
        duration_seconds=max(1, int(reopen_minutes or 5)) * 60,
    )

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
