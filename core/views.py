from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect, render

from .forms import AccountInfoForm, RegistrationForm
from .models import User


SAMPLE_TESTS = [
    {
        "id": 1,
        "title": "Mathematics - Algebra",
        "date": "18 June 2026",
        "length": "45 minutes",
        "status": "Active",
    },
    {
        "id": 2,
        "title": "Biology - Cell Structure",
        "date": "23 June 2026",
        "length": "60 minutes",
        "status": "Active",
    },
    {
        "id": 3,
        "title": "History - Industrial Revolution",
        "date": "10 June 2026",
        "length": "40 minutes",
        "status": "Completed",
    },
]


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
    return render(
        request,
        "core/test_overview.html",
        {"active_page": "overview", "tests": SAMPLE_TESTS},
    )


@login_required
def test_detail(request, test_id):
    test = next((item for item in SAMPLE_TESTS if item["id"] == test_id), None)
    if test is None:
        raise Http404("Test not found.")

    return render(
        request,
        "core/test_detail.html",
        {"active_page": "overview", "test": test},
    )


@login_required
def test_creation(request):
    if request.user.role != User.Role.TEACHER:
        return HttpResponseForbidden("Only teacher accounts can access test creation.")

    return render(
        request,
        "core/test_creation.html",
        {"active_page": "creation"},
    )


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
