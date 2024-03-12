from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser

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


class LandlordSignupForm(UserCreationForm):
    pdf_file = forms.FileField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "full_name",
            "email",
            "phone_number",
            "city",
            "password1",
            "password2",
            # "user_type",
            "pdf_file",
        )

    def _init_(self, *args, **kwargs):
        super(LandlordSignupForm, self)._init_(*args, **kwargs)
        self.fields["user_type"].initial = CustomUser.LANDLORD
        self.fields[
            "user_type"
        ].widget = forms.HiddenInput()  # Hide the user_type field
