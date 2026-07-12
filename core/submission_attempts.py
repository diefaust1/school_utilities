from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from .forms import TestSubmissionForm
from .models import StudentAnswer, Test, TestAttempt, TestAttemptAnswer, TestSubmission, User


@dataclass(frozen=True)
class SubmissionAttempt:
    test: Test
    student: User
    active_submission: TestSubmission | None
    latest_submission: TestSubmission | None
    active_attempt: TestAttempt | None

    @classmethod
    def load(cls, *, test: Test, student: User) -> "SubmissionAttempt":
        finalize_expired_attempts(student=student, test=test)
        student_submissions = TestSubmission.objects.filter(
            test=test,
            student=student,
        ).prefetch_related("answers")
        active_submission = student_submissions.filter(
            status=TestSubmission.Status.SUBMITTED,
        ).first()
        active_attempt = (
            TestAttempt.objects.filter(
                test=test,
                student=student,
                status=TestAttempt.Status.IN_PROGRESS,
            )
            .prefetch_related("answers")
            .first()
        )

        return cls(
            test=test,
            student=student,
            active_submission=active_submission,
            latest_submission=student_submissions.first(),
            active_attempt=active_attempt,
        )

    @property
    def can_submit(self) -> bool:
        return self.test.is_active and self.active_submission is None and self.active_attempt is not None

    @property
    def display_submission(self) -> TestSubmission | None:
        return self.active_submission or self.latest_submission

    @property
    def has_started(self) -> bool:
        return self.active_attempt is not None

    @property
    def remaining_seconds(self) -> int | None:
        if self.active_attempt is None:
            return None
        return remaining_seconds(self.active_attempt)

    def build_form(self, data=None) -> TestSubmissionForm:
        return TestSubmissionForm(
            data,
            test=self.test,
            user=self.student,
            disabled=not self.can_submit,
            initial_submission=self.display_submission if self.active_attempt is None else None,
            initial_attempt=self.active_attempt,
        )

    def question_fields(self, form: TestSubmissionForm):
        return [
            (question, form[form.answer_field_name(question)])
            for question in form.questions
        ]

    @transaction.atomic
    def save_draft(self, form: TestSubmissionForm) -> None:
        if self.active_attempt is None:
            raise SubmissionUnavailable("This test has not been started.")
        if not form.is_valid():
            raise ValueError("SubmissionAttempt.save_draft() requires a valid form.")

        save_attempt_draft(attempt=self.active_attempt, form=form)

    @transaction.atomic
    def submit(self, form: TestSubmissionForm) -> TestSubmission:
        if not self.can_submit:
            raise SubmissionUnavailable("This test is not currently available.")
        if not form.is_valid():
            raise ValueError("SubmissionAttempt.submit() requires a valid form.")

        self.save_draft(form)
        return finalize_attempt(self.active_attempt)


def start_or_continue_attempt(*, test: Test, student: User) -> TestAttempt:
    finalize_expired_attempts(student=student, test=test)
    active_submission = TestSubmission.objects.filter(
        test=test,
        student=student,
        status=TestSubmission.Status.SUBMITTED,
    ).first()
    if active_submission is not None:
        raise SubmissionUnavailable("This test has already been submitted.")

    active_attempt = TestAttempt.objects.filter(
        test=test,
        student=student,
        status=TestAttempt.Status.IN_PROGRESS,
    ).first()
    if active_attempt is not None:
        return active_attempt

    latest_submission = (
        TestSubmission.objects.filter(test=test, student=student)
        .prefetch_related("answers")
        .first()
    )
    source_submission = (
        latest_submission
        if latest_submission is not None and latest_submission.status == TestSubmission.Status.REOPENED
        else None
    )
    duration_seconds = (
        source_submission.reopen_duration_seconds
        if source_submission is not None and source_submission.reopen_duration_seconds is not None
        else test.length_minutes * 60
    )
    attempt = TestAttempt.objects.create(
        test=test,
        student=student,
        source_submission=source_submission,
        duration_seconds=duration_seconds,
        student_first_name=source_submission.student_first_name if source_submission else student.first_name,
        student_last_name=source_submission.student_last_name if source_submission else student.last_name,
    )

    if source_submission is not None:
        TestAttemptAnswer.objects.bulk_create(
            [
                TestAttemptAnswer(
                    attempt=attempt,
                    question=answer.question,
                    answer_text=answer.answer_text,
                )
                for answer in source_submission.answers.all()
            ]
        )

    return attempt


def save_attempt_draft(*, attempt: TestAttempt, form: TestSubmissionForm) -> None:
    attempt.student_first_name = form.cleaned_data["student_first_name"]
    attempt.student_last_name = form.cleaned_data["student_last_name"]
    attempt.save(update_fields=("student_first_name", "student_last_name"))

    for question in form.questions:
        TestAttemptAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={"answer_text": form.cleaned_data.get(form.answer_field_name(question), "")},
        )


@transaction.atomic
def finalize_attempt(attempt: TestAttempt) -> TestSubmission:
    attempt = TestAttempt.objects.select_for_update().prefetch_related("answers").get(pk=attempt.pk)
    if attempt.status != TestAttempt.Status.IN_PROGRESS:
        if attempt.submitted_submission is None:
            raise SubmissionUnavailable("This attempt has already been closed.")
        return attempt.submitted_submission

    submission = TestSubmission.objects.create(
        test=attempt.test,
        student=attempt.student,
        student_first_name=attempt.student_first_name,
        student_last_name=attempt.student_last_name,
        status=TestSubmission.Status.SUBMITTED,
        remaining_seconds=remaining_seconds(attempt),
    )
    draft_answers = {answer.question_id: answer.answer_text for answer in attempt.answers.all()}
    StudentAnswer.objects.bulk_create(
        [
            StudentAnswer(
                submission=submission,
                question=question,
                answer_text=draft_answers.get(question.id, ""),
            )
            for question in attempt.test.questions.all()
        ]
    )
    attempt.status = TestAttempt.Status.SUBMITTED
    attempt.submitted_submission = submission
    attempt.save(update_fields=("status", "submitted_submission"))
    return submission


def finalize_expired_attempts(*, student: User | None = None, test: Test | None = None) -> None:
    attempts = TestAttempt.objects.filter(status=TestAttempt.Status.IN_PROGRESS)
    if student is not None:
        attempts = attempts.filter(student=student)
    if test is not None:
        attempts = attempts.filter(test=test)

    for attempt in attempts:
        if remaining_seconds(attempt) == 0:
            finalize_attempt(attempt)


def remaining_seconds(attempt: TestAttempt) -> int:
    elapsed = int((timezone.now() - attempt.started_at).total_seconds())
    return max(0, attempt.duration_seconds - elapsed)


class SubmissionUnavailable(Exception):
    pass
