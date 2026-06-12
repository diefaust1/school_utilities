from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountTests(TestCase):
    def test_user_uses_email_as_login_identifier(self):
        user = User.objects.create_user(
            email="student@example.com",
            password="test-password",
        )

        self.assertEqual(user.email, "student@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.check_password("test-password"))

    def test_registration_creates_and_logs_in_student(self):
        response = self.client.post(
            reverse("registration"),
            {
                "email": "new-student@example.com",
                "role": User.Role.STUDENT,
                "password": "four",
                "password_confirm": "four",
            },
        )

        user = User.objects.get(email="new-student@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertRedirects(response, reverse("test-overview"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_registration_creates_teacher_with_teacher_access(self):
        response = self.client.post(
            reverse("registration"),
            {
                "email": "new-teacher@example.com",
                "role": User.Role.TEACHER,
                "password": "four",
                "password_confirm": "four",
            },
        )

        user = User.objects.get(email="new-teacher@example.com")
        self.assertEqual(user.role, User.Role.TEACHER)
        self.assertRedirects(response, reverse("test-overview"))

        response = self.client.get(reverse("test-creation"))
        self.assertEqual(response.status_code, 200)

    def test_registration_rejects_password_shorter_than_four_characters(self):
        response = self.client.post(
            reverse("registration"),
            {
                "email": "new-student@example.com",
                "role": User.Role.STUDENT,
                "password": "123",
                "password_confirm": "123",
            },
        )

        self.assertContains(response, "Ensure this value has at least 4 characters")
        self.assertFalse(User.objects.exists())

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(
            email="student@example.com",
            password="test-password",
        )

        response = self.client.post(
            reverse("registration"),
            {
                "email": "STUDENT@example.com",
                "role": User.Role.STUDENT,
                "password": "test-password",
                "password_confirm": "test-password",
            },
        )

        self.assertContains(response, "An account with this e-mail address already exists.")
        self.assertEqual(User.objects.count(), 1)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("registration"),
            {
                "email": "student@example.com",
                "role": User.Role.STUDENT,
                "password": "test-password",
                "password_confirm": "different-password",
            },
        )

        self.assertContains(response, "The passwords do not match.")
        self.assertFalse(User.objects.exists())

    def test_registration_rejects_unknown_role(self):
        response = self.client.post(
            reverse("registration"),
            {
                "email": "user@example.com",
                "role": "administrator",
                "password": "four",
                "password_confirm": "four",
            },
        )

        self.assertContains(response, "Select a valid choice")
        self.assertFalse(User.objects.exists())


class PageAccessTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="student@example.com",
            password="test-password",
            first_name="Example",
            last_name="Student",
        )
        self.teacher = User.objects.create_user(
            email="teacher@example.com",
            password="test-password",
            first_name="Example",
            last_name="Teacher",
            role=User.Role.TEACHER,
        )

    def test_protected_page_redirects_to_login(self):
        response = self.client.get(reverse("test-overview"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('test-overview')}",
        )

    def test_valid_login_redirects_to_overview(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.student.email.upper(), "password": "test-password"},
        )

        self.assertRedirects(response, reverse("test-overview"))

    def test_invalid_login_shows_generic_error_and_keeps_email(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.student.email, "password": "incorrect"},
        )

        self.assertContains(response, "The e-mail address or password is incorrect.")
        self.assertContains(response, f'value="{self.student.email}"')

    def test_student_cannot_access_test_creation(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("test-creation"))

        self.assertEqual(response.status_code, 403)

    def test_teacher_can_access_test_creation(self):
        self.client.force_login(self.teacher)

        response = self.client.get(reverse("test-creation"))

        self.assertContains(response, "Test Creation")

    def test_user_can_update_first_and_last_name(self):
        self.client.force_login(self.student)

        response = self.client.post(
            reverse("account-info"),
            {"first_name": "Updated", "last_name": "Name"},
        )

        self.assertRedirects(response, f"{reverse('account-info')}?saved=1")
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Updated")
        self.assertEqual(self.student.last_name, "Name")

    def test_account_page_shows_save_confirmation(self):
        self.client.force_login(self.student)

        response = self.client.get(f"{reverse('account-info')}?saved=1")

        self.assertContains(response, "Your name was saved.")

    def test_account_update_rejects_name_longer_than_model_limit(self):
        self.client.force_login(self.student)

        response = self.client.post(
            reverse("account-info"),
            {"first_name": "a" * 151, "last_name": "Student"},
        )

        self.assertContains(response, "Ensure this value has at most 150 characters")
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Example")

    def test_unknown_test_returns_404(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("test-detail", args=[999]))

        self.assertEqual(response.status_code, 404)
