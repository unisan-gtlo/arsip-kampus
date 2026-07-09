from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "masukkan username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "masukkan password"})
    )


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        min_length=6,
    )

    class Meta:
        model = User
        fields = ["username", "password", "nama", "role"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "nama": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
