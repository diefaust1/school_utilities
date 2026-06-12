from django.urls import path

from . import views


urlpatterns = [
    path("", views.login_page, name="login"),
    path("register/", views.registration_page, name="registration"),
    path("tests/", views.test_overview, name="test-overview"),
    path("tests/<int:test_id>/", views.test_detail, name="test-detail"),
    path("tests/create/", views.test_creation, name="test-creation"),
    path("account/", views.account_info, name="account-info"),
    path("logout/", views.logout_page, name="logout"),
]
