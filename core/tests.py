from django.test import TestCase  # type: ignore[import]
from django.urls import reverse  # type: ignore[import]

from .models import Question, StudentAnswer, Test, TestSubmission, User


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

    def test_everyone_can_see_database_backed_tests(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("test-overview"))

        self.assertContains(response, "Mathematics - Basics")
        self.assertContains(response, "Biology - Cell Structure")
        self.assertContains(response, "45 minutes")

    def test_seeded_tests_have_three_complete_questions(self):
        tests = Test.objects.filter(
            title__in=["Mathematics - Basics", "Biology - Cell Structure"]
        )

        self.assertEqual(tests.count(), 2)

        for test in tests:
            self.assertEqual(test.questions.count(), 3)
            self.assertEqual(
                test.questions.filter(answer_type=Question.AnswerType.MULTIPLE_CHOICE).count(),
                2,
            )
            self.assertEqual(
                test.questions.filter(answer_type=Question.AnswerType.FREE_TEXT).count(),
                1,
            )

            for question in test.questions.all():
                self.assertTrue(question.title)
                self.assertTrue(question.description)
                self.assertGreater(question.points, 0)
                self.assertIn(question.answer_type, Question.AnswerType.values)

    def test_biology_test_can_be_opened(self):
        self.client.force_login(self.student)
        test = Test.objects.get(title="Biology - Cell Structure")

        response = self.client.get(reverse("test-detail", args=[test.pk]))

        self.assertContains(response, "Cell Organelle")
        self.assertContains(response, "Explain Cell Membranes")

    def test_student_can_submit_test_with_name_and_answers(self):
        self.client.force_login(self.student)
        test = Test.objects.get(title="Mathematics - Basics")
        questions = list(test.questions.all())

        response = self.client.post(
            reverse("test-detail", args=[test.pk]),
            {
                "student_first_name": "Submitted",
                "student_last_name": "Student",
                f"question_{questions[0].pk}": "B",
                f"question_{questions[1].pk}": "C",
                f"question_{questions[2].pk}": "Because substituting the value should make both sides equal.",
            },
        )

        self.assertRedirects(response, f"{reverse('test-detail', args=[test.pk])}?submitted=1")
        submission = TestSubmission.objects.get(test=test, student=self.student)
        self.assertEqual(submission.student_first_name, "Submitted")
        self.assertEqual(submission.student_last_name, "Student")
        self.assertEqual(submission.answers.count(), 3)
        self.assertTrue(
            StudentAnswer.objects.filter(
                submission=submission,
                question=questions[2],
                answer_text__contains="substituting",
            ).exists()
        )

    def test_submitted_test_is_marked_on_overview(self):
        test = Test.objects.get(title="Mathematics - Basics")
        TestSubmission.objects.create(
            test=test,
            student=self.student,
            student_first_name="Example",
            student_last_name="Student",
        )
        self.client.force_login(self.student)

        response = self.client.get(reverse("test-overview"))

        self.assertContains(response, "Submitted")
        self.assertContains(response, "test-card-submitted")

    def test_submitted_test_detail_keeps_saved_answers_visible(self):
        test = Test.objects.get(title="Mathematics - Basics")
        questions = list(test.questions.all())
        submission = TestSubmission.objects.create(
            test=test,
            student=self.student,
            student_first_name="Saved",
            student_last_name="Student",
        )
        StudentAnswer.objects.create(
            submission=submission,
            question=questions[0],
            answer_text="B",
        )
        StudentAnswer.objects.create(
            submission=submission,
            question=questions[1],
            answer_text="C",
        )
        StudentAnswer.objects.create(
            submission=submission,
            question=questions[2],
            answer_text="A saved free-text answer.",
        )
        self.client.force_login(self.student)

        response = self.client.get(reverse("test-detail", args=[test.pk]))

        self.assertContains(response, 'value="Saved"')
        self.assertContains(response, 'value="Student"')
        self.assertContains(response, "A saved free-text answer.")
        self.assertContains(response, "Already submitted")
        self.assertContains(response, "disabled")
        self.assertContains(response, "Save as PDF")

    def test_reopened_test_prefills_previous_name_and_answers(self):
        test = Test.objects.get(title="Mathematics - Basics")
        questions = list(test.questions.all())
        submission = TestSubmission.objects.create(
            test=test,
            student=self.student,
            student_first_name="Previous",
            student_last_name="Name",
            status=TestSubmission.Status.REOPENED,
            reopened_by=self.teacher,
        )
        StudentAnswer.objects.create(
            submission=submission,
            question=questions[0],
            answer_text="B",
        )
        StudentAnswer.objects.create(
            submission=submission,
            question=questions[1],
            answer_text="C",
        )
        StudentAnswer.objects.create(
            submission=submission,
            question=questions[2],
            answer_text="Previous answer.",
        )
        self.client.force_login(self.student)

        response = self.client.get(reverse("test-detail", args=[test.pk]))

        self.assertContains(response, 'value="Previous"')
        self.assertContains(response, 'value="Name"')
        self.assertContains(response, "Previous answer.")
        self.assertContains(response, "Submit test")
        self.assertNotContains(response, "Already submitted")

    def test_student_cannot_submit_same_test_twice(self):
        self.client.force_login(self.student)
        test = Test.objects.get(title="Mathematics - Basics")
        questions = list(test.questions.all())
        TestSubmission.objects.create(
            test=test,
            student=self.student,
            student_first_name="Example",
            student_last_name="Student",
        )

        response = self.client.post(
            reverse("test-detail", args=[test.pk]),
            {
                "student_first_name": "Again",
                "student_last_name": "Student",
                f"question_{questions[0].pk}": "B",
                f"question_{questions[1].pk}": "C",
                f"question_{questions[2].pk}": "Again.",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            TestSubmission.objects.filter(test=test, student=self.student).count(),
            1,
        )

    def test_inactive_test_cannot_be_submitted(self):
        self.client.force_login(self.student)
        test = Test.objects.get(title="Mathematics - Basics")
        test.is_active = False
        test.save(update_fields=("is_active",))
        questions = list(test.questions.all())

        response = self.client.post(
            reverse("test-detail", args=[test.pk]),
            {
                "student_first_name": "Example",
                "student_last_name": "Student",
                f"question_{questions[0].pk}": "B",
                f"question_{questions[1].pk}": "C",
                f"question_{questions[2].pk}": "Inactive.",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(TestSubmission.objects.exists())

    def test_teacher_can_reopen_submission_and_student_can_submit_again(self):
        test = Test.objects.get(title="Mathematics - Basics")
        questions = list(test.questions.all())
        submission = TestSubmission.objects.create(
            test=test,
            student=self.student,
            student_first_name="Example",
            student_last_name="Student",
        )
        self.client.force_login(self.teacher)

        response = self.client.post(reverse("reopen-submission", args=[submission.pk]))

        self.assertRedirects(response, reverse("test-submissions"))
        submission.refresh_from_db()
        self.assertEqual(submission.status, TestSubmission.Status.REOPENED)
        self.assertEqual(submission.reopened_by, self.teacher)

        self.client.force_login(self.student)
        response = self.client.post(
            reverse("test-detail", args=[test.pk]),
            {
                "student_first_name": "Second",
                "student_last_name": "Attempt",
                f"question_{questions[0].pk}": "B",
                f"question_{questions[1].pk}": "C",
                f"question_{questions[2].pk}": "Second attempt.",
            },
        )

        self.assertRedirects(response, f"{reverse('test-detail', args=[test.pk])}?submitted=1")
        self.assertEqual(
            TestSubmission.objects.filter(test=test, student=self.student).count(),
            2,
        )
        self.assertTrue(
            TestSubmission.objects.filter(
                test=test,
                student=self.student,
                status=TestSubmission.Status.SUBMITTED,
                student_first_name="Second",
            ).exists()
        )

    def test_teacher_can_deactivate_and_activate_test(self):
        test = Test.objects.get(title="Mathematics - Basics")
        self.client.force_login(self.teacher)

        response = self.client.post(
            reverse("toggle-test-activation", args=[test.pk]),
            {"is_active": "false"},
        )

        self.assertRedirects(response, reverse("test-overview"))
        test.refresh_from_db()
        self.assertFalse(test.is_active)

        response = self.client.post(
            reverse("toggle-test-activation", args=[test.pk]),
            {"is_active": "true"},
        )

        self.assertRedirects(response, reverse("test-overview"))
        test.refresh_from_db()
        self.assertTrue(test.is_active)

    def test_teacher_sees_activation_button_on_overview(self):
        self.client.force_login(self.teacher)

        response = self.client.get(reverse("test-overview"))

        self.assertContains(response, "Deactivate test")

    def test_student_cannot_toggle_test_activation_or_reopen(self):
        test = Test.objects.get(title="Mathematics - Basics")
        submission = TestSubmission.objects.create(
            test=test,
            student=self.student,
            student_first_name="Example",
            student_last_name="Student",
        )
        self.client.force_login(self.student)

        activation_response = self.client.post(
            reverse("toggle-test-activation", args=[test.pk]),
            {"is_active": "false"},
        )
        reopen_response = self.client.post(reverse("reopen-submission", args=[submission.pk]))

        self.assertEqual(activation_response.status_code, 403)
        self.assertEqual(reopen_response.status_code, 403)

    def test_submission_requires_all_answers(self):
        self.client.force_login(self.student)
        test = Test.objects.get(title="Mathematics - Basics")
        questions = list(test.questions.all())

        response = self.client.post(
            reverse("test-detail", args=[test.pk]),
            {
                "student_first_name": "Submitted",
                "student_last_name": "Student",
                f"question_{questions[0].pk}": "B",
            },
        )

        self.assertContains(response, "This field is required.")
        self.assertFalse(TestSubmission.objects.exists())

    def test_teacher_can_view_saved_submissions(self):
        test = Test.objects.get(title="Mathematics - Basics")
        submission = TestSubmission.objects.create(
            test=test,
            student=self.student,
            student_first_name="Example",
            student_last_name="Student",
        )
        question = test.questions.first()
        StudentAnswer.objects.create(
            submission=submission,
            question=question,
            answer_text="B",
        )
        self.client.force_login(self.teacher)

        response = self.client.get(reverse("test-submissions"))

        self.assertContains(response, "Example Student")
        self.assertContains(response, "Mathematics - Basics")
        self.assertContains(response, "<details", html=False)
        self.assertContains(response, "Reopen")
        self.assertContains(response, "B")

    def test_student_cannot_view_saved_submissions(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("test-submissions"))

        self.assertEqual(response.status_code, 403)

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
