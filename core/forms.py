from django import forms
from django.db import transaction

from .models import Question, StudentAnswer, Test, TestSubmission, User


class RegistrationForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=User.Role.choices)
    # TODO: Restore a stronger password policy before production deployment.
    password = forms.CharField(min_length=4, widget=forms.PasswordInput)
    password_confirm = forms.CharField(min_length=4, widget=forms.PasswordInput)

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this e-mail address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            self.add_error("password_confirm", "The passwords do not match.")
        return cleaned_data

    def save(self) -> User:
        if not self.is_valid():
            raise ValueError("RegistrationForm.save() requires a valid form.")

        return User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            role=self.cleaned_data["role"],
        )


class AccountInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
        }


class TestActivationForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ("is_active",)


class TestSubmissionForm(forms.Form):
    student_first_name = forms.CharField(max_length=150)
    student_last_name = forms.CharField(max_length=150)

    def __init__(
        self,
        *args,
        test: Test,
        user: User,
        disabled: bool = False,
        initial_submission: TestSubmission | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.test = test
        self.user = user
        self.questions = list(test.questions.all())
        self.disabled = disabled
        answer_initials = {}

        if initial_submission is not None:
            answer_initials = {
                answer.question_id: answer.answer_text
                for answer in initial_submission.answers.all()
            }

        self.fields["student_first_name"].initial = (
            initial_submission.student_first_name
            if initial_submission is not None
            else user.first_name
        )
        self.fields["student_last_name"].initial = (
            initial_submission.student_last_name
            if initial_submission is not None
            else user.last_name
        )

        for question in self.questions:
            field_name = self.answer_field_name(question)
            label = f"{question.title} answer"

            if question.answer_type == Question.AnswerType.MULTIPLE_CHOICE:
                self.fields[field_name] = forms.ChoiceField(
                    choices=question.options,
                    label=label,
                    widget=forms.RadioSelect,
                )
            else:
                self.fields[field_name] = forms.CharField(
                    label=label,
                    widget=forms.Textarea(attrs={"rows": 6}),
                )

            if question.id in answer_initials:
                self.fields[field_name].initial = answer_initials[question.id]

            if disabled:
                self.fields[field_name].disabled = True

        if disabled:
            self.fields["student_first_name"].disabled = True
            self.fields["student_last_name"].disabled = True

    @staticmethod
    def answer_field_name(question: Question) -> str:
        return f"question_{question.id}"

    @transaction.atomic
    def save(self) -> TestSubmission:
        if not self.is_valid():
            raise ValueError("TestSubmissionForm.save() requires a valid form.")

        submission = TestSubmission.objects.create(
            test=self.test,
            student=self.user,
            student_first_name=self.cleaned_data["student_first_name"],
            student_last_name=self.cleaned_data["student_last_name"],
            status=TestSubmission.Status.SUBMITTED,
        )

        answers = [
            StudentAnswer(
                submission=submission,
                question=question,
                answer_text=self.cleaned_data[self.answer_field_name(question)],
            )
            for question in self.questions
        ]
        StudentAnswer.objects.bulk_create(answers)
        return submission
