from __future__ import annotations

from dataclasses import dataclass

from .models import Question, StudentAnswer, Test, TestSubmission
from .submission_attempts import finalize_expired_attempts


@dataclass(frozen=True)
class ReviewQuestion:
    question: Question
    answer_text: str


@dataclass(frozen=True)
class ReviewSubmission:
    submission: TestSubmission
    questions: list[ReviewQuestion]

    @property
    def can_reopen(self) -> bool:
        return self.submission.status == TestSubmission.Status.SUBMITTED

    @property
    def status_class(self) -> str:
        if self.submission.status == TestSubmission.Status.SUBMITTED:
            return "status-submitted"
        return "status-reopened"

    @property
    def remaining_time_display(self) -> str:
        if self.submission.remaining_seconds is None:
            return "Not tracked"
        minutes = self.submission.remaining_seconds // 60
        seconds = self.submission.remaining_seconds % 60
        return f"{minutes}:{seconds:02d}"


@dataclass(frozen=True)
class ReviewTest:
    test: Test
    submissions: list[ReviewSubmission]


def load_teacher_review_tests() -> list[ReviewTest]:
    finalize_expired_attempts()
    tests = Test.objects.prefetch_related(
        "questions",
        "submissions__student",
        "submissions__answers__question",
    ).all()

    return [
        ReviewTest(
            test=test,
            submissions=[
                _build_review_submission(test, submission)
                for submission in test.submissions.all()
            ],
        )
        for test in tests
    ]


def reopen_submission(*, submission: TestSubmission, teacher, duration_seconds: int = 300) -> None:
    if submission.status != TestSubmission.Status.SUBMITTED:
        return

    from django.utils import timezone

    submission.status = TestSubmission.Status.REOPENED
    submission.reopened_at = timezone.now()
    submission.reopened_by = teacher
    submission.reopen_duration_seconds = duration_seconds
    submission.save(update_fields=("status", "reopened_at", "reopened_by", "reopen_duration_seconds"))


def _build_review_submission(test: Test, submission: TestSubmission) -> ReviewSubmission:
    answers_by_question_id = {
        answer.question_id: answer
        for answer in submission.answers.all()
    }
    return ReviewSubmission(
        submission=submission,
        questions=[
            ReviewQuestion(
                question=question,
                answer_text=_display_answer(question, answers_by_question_id.get(question.id)),
            )
            for question in test.questions.all()
        ],
    )


def _display_answer(question: Question, answer: StudentAnswer | None) -> str:
    if answer is None:
        return ""

    if question.answer_type != Question.AnswerType.MULTIPLE_CHOICE:
        return answer.answer_text

    options = dict(question.options)
    selected_option = options.get(answer.answer_text)
    if selected_option is None:
        return answer.answer_text
    return f"{answer.answer_text}. {selected_option}"
