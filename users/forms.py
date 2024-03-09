from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    city = forms.CharField(max_length=100, required=True)
    s3_doclink = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "full_name",
            "phone_number",
            "city",
            "s3_doclink",
            "password1",
            "password2",
        )
