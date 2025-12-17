from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class FollowUserForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur à suivre",
        max_length=150,
    )
