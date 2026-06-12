from django import forms

from .models import User


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
