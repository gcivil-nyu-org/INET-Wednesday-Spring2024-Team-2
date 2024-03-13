from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class UserSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    city = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "full_name",
            "phone_number",
            "city",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not email.endswith("@nyu.edu"):
            raise ValidationError("Oops!! Only NYU email addresses are supported.")
        return email


class LandlordSignupForm(UserCreationForm):
    pdf_file = forms.FileField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "full_name",
            "phone_number",
            "city",
            "password1",
            "password2",
            # "user_type",
            "pdf_file",
        )

    # def _init_(self, *args, **kwargs):
    #     super(LandlordSignupForm, self)._init_(*args, **kwargs)
    #     self.fields["user_type"].initial = CustomUser.LANDLORD
    #     self.fields[
    #         "user_type"
    #     ].widget = forms.HiddenInput()  # Hide the user_type field

    def _init_(self, *args, **kwargs):
        super(LandlordSignupForm, self)._init_(*args, **kwargs)
        # No need to set user_type initial value here, as it will be set in save.

    def save(self, commit=True):
        user = super(LandlordSignupForm, self).save(commit=False)
        user.user_type = CustomUser.LANDLORD  # Set user_type to LANDLORD

        if commit:
            user.save()
            self.save_m2m()  # Call save_m2m if there are many-to-many fields that need to be saved.

        return user


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                """This email does not exist in our records.
                                        Please make sure you entered it correctly,
                                        or sign up for a new account
                                        if you haven't already."""
            )
        return email


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
