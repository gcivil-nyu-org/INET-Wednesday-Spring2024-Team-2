from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser, Rental_Listings
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
            raise ValidationError("Oops! Only NYU email addresses are supported.")
        if User.objects.filter(username=self.cleaned_data["email"]).exists():
            raise ValidationError("Email already exists. Please use a different one.")
        return email


class LandlordSignupForm(UserCreationForm):
    pdf_file = forms.FileField(required=False, label="OwnerShip Document")  #

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
            self.save_m2m()

        return user


class RentalListingForm(forms.ModelForm):

    photo = forms.ImageField(required=False)  # 根据需要设置required为True或False
    class Meta:
        model = Rental_Listings
        fields = ['address', 'price', 'link', 'sq_ft', 'rooms', 'beds', 'baths', 'unit_type',
                  'neighborhood', 'central_air_conditioning', 'dishwasher', 'doorman', 'elevator',
                  'furnished', 'parking_available', 'washer_dryer_in_unit',
                  'Submitted_date', 'Availability_Date','photo']
        widgets = {
            'Submitted_date': forms.DateInput(attrs={'type': 'date'}),
            'Availability_Date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
