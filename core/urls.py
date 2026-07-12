from django.urls import path

from . import views


urlpatterns = [
    path("", views.login_page, name="login"),
    path("register/", views.registration_page, name="registration"),
    path("tests/", views.test_overview, name="test-overview"),
    path("tests/<int:test_id>/start/", views.start_test, name="start-test"),
    path("tests/<int:test_id>/autosave/", views.autosave_test_attempt, name="autosave-test-attempt"),
    path("tests/<int:test_id>/", views.test_detail, name="test-detail"),
    path("tests/create/", views.test_creation, name="test-creation"),
    path("submissions/", views.test_submissions, name="test-submissions"),
    path("submissions/<int:submission_id>/reopen/", views.reopen_submission, name="reopen-submission"),
    path("tests/<int:test_id>/activation/", views.toggle_test_activation, name="toggle-test-activation"),
    path("account/", views.account_info, name="account-info"),
    path("logout/", views.logout_page, name="logout"),
]
