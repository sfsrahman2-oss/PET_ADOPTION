from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import AdoptionRequest


class BootstrapMixin:
    def _style(self):
        for f in self.fields.values():
            if isinstance(f.widget, forms.RadioSelect):
                continue
            f.widget.attrs["class"] = "form-control"


class LoginForm(BootstrapMixin, AuthenticationForm):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._style()


class RegisterForm(BootstrapMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._style()


class AdoptionForm(BootstrapMixin, forms.ModelForm):
    previous_pet_experience = forms.TypedChoiceField(
        label="Have you owned a pet before?",
        choices=[(True, "Yes"), (False, "No")],
        coerce=lambda v: v == "True",
        widget=forms.RadioSelect,
        initial=False,
    )

    class Meta:
        model = AdoptionRequest
        fields = ["address", "phone", "reason", "previous_pet_experience", "message"]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 3}),
            "message": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._style()
