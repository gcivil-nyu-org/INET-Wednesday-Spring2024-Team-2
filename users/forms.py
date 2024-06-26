import re
from datetime import date, timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser, Rental_Listings
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm
from django.utils import timezone

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

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if len(phone_number) != 10 or not phone_number.isdigit():
            raise ValidationError("Phone number must be 10 digits.")
        return phone_number


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
    ROOMS_CHOICES = [(i, str(i)) for i in range(1, 11)]
    BATHS_CHOICES = [(i * 0.5, str(i * 0.5)) for i in range(2, 21)]

    UNIT_TYPE_CHOICES = [
        ("Apartment", "Apartment"),
        ("House", "House"),
        ("Multi-family", "Multi-family"),
        ("Condo", "Condo"),
        ("Rental Unit", "Rental Unit"),
        ("Building", "Building"),
        ("Townhouse", "Townhouse"),
        ("Co-op", "Co-op"),
    ]
    NEIGHBORHOOD_CHOICES = [
        ("Manhattan", "Manhattan"),
        ("Brooklyn", "Brooklyn"),
        ("Upper East Side", "Upper East Side"),
        ("Upper West Side", "Upper West Side"),
        ("Midtown", "Midtown"),
        ("Harlem", "Harlem"),
        ("Chelsea", "Chelsea"),
        ("Greenwich Village", "Greenwich Village"),
        ("Soho", "Soho"),
        ("East Village", "East Village"),
        ("Lower East Side", "Lower East Side"),
        ("Williamsburg", "Williamsburg"),
        ("Bushwick", "Bushwick"),
        ("Park Slope", "Park Slope"),
        ("Brooklyn Heights", "Brooklyn Heights"),
        ("Red Hook", "Red Hook"),
        ("Astoria", "Astoria"),
        ("Long Island City", "Long Island City"),
        ("Flushing", "Flushing"),
        ("Jamaica", "Jamaica"),
        ("Forest Hills", "Forest Hills"),
        ("Riverdale", "Riverdale"),
        ("Fordham", "Fordham"),
        ("Concourse", "Concourse"),
        ("Throgs Neck", "Throgs Neck"),
        ("St. George", "St. George"),
        ("Tottenville", "Tottenville"),
        ("Stapleton", "Stapleton"),
    ]

    BOROUGH_CHOICES = [
        ("Manhattan", "Manhattan"),
        ("Brooklyn", "Brooklyn"),
        ("Queens", "Queens"),
        ("Bronx", "Bronx"),
        ("Staten Island", "Staten Island"),
    ]
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "id": "id_address",
                "placeholder": "Enter your address",
                "autocomplete": "off",
            }
        )
    )
    rooms = forms.ChoiceField(choices=ROOMS_CHOICES)
    beds = forms.ChoiceField(choices=ROOMS_CHOICES)
    baths = forms.ChoiceField(choices=BATHS_CHOICES)
    unit_type = forms.ChoiceField(choices=UNIT_TYPE_CHOICES)
    neighborhood = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"id": "id_neighborhood"})
    )
    borough = forms.ChoiceField(
        choices=BOROUGH_CHOICES, widget=forms.Select(attrs={"id": "id_borough"})
    )
    photo = forms.ImageField(
        required=False,
        label="Images",
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )
    latitude = forms.FloatField(
        widget=forms.HiddenInput(attrs={"readonly": "readonly"})
    )
    longitude = forms.FloatField(
        widget=forms.HiddenInput(attrs={"readonly": "readonly"})
    )
    zipcode = forms.CharField(
        required=True,
        label="Zip",
        widget=forms.TextInput(attrs={"id": "id_zipcode", "placeholder": ""}),
    )
    sq_ft = forms.IntegerField(required=True, label="Area(sqft)")
    Availability_Date = forms.DateField(
        required=True, widget=forms.DateInput(attrs={"type": "date"})
    )
    apt_no = forms.CharField(
        required=False,
        label="Apt#",
        widget=forms.TextInput(attrs={"id": "id_aptNo", "placeholder": ""}),
    )

    def __init__(self, *args, **kwargs):
        super(RentalListingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.layout = Layout(
            Row(
                Column("address", css_class="form-group col-md-8 mb-0"),
                Column("zipcode", css_class="form-group col-md-2 mb-0"),
                Column("apt_no", css_class="form-group col-md-2 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("price", css_class="form-group col-md-4 mb-0"),
                Column("sq_ft", css_class="form-group col-md-4 mb-0"),
                Column("broker_fee", css_class="form-group col-md-4 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("rooms", css_class="form-group col-md-4 mb-0"),
                Column("beds", css_class="form-group col-md-4 mb-0"),
                Column("baths", css_class="form-group col-md-4 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("neighborhood", css_class="form-group col-md-4 mb-0"),
                Column("borough", css_class="form-group col-md-4 mb-0"),
                Column("unit_type", css_class="form-group col-md-4 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("dishwasher", css_class="form-group col-md-6 mb-0"),
                Column("doorman", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column(
                    "central_air_conditioning", css_class="form-group col-md-6 mb-0"
                ),
                Column("furnished", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Row(
                Column("parking_available", css_class="form-group col-md-6 mb-0"),
                Column("washer_dryer_in_unit", css_class="form-group col-md-6 mb-0"),
                css_class="form-row",
            ),
            Column("elevator", css_class="form-group col-md-4 mb-0"),
            "Availability_Date",
            Row(
                Column(
                    "latitude", css_class="form-group col-md-4 mb-0 align-self-end"
                ),  # Add 'align-self-end' class
                Column(
                    "longitude", css_class="form-group col-md-4 mb-0 align-self-end"
                ),  # Add 'align-self-end' class
                css_class="form-row location-row",
            ),
            Field("photo", multiple=True),
            Submit("submit", "Submit", css_class="btn btn-primary form-button1"),
        )

    class Meta:
        model = Rental_Listings
        fields = [
            "address",
            "zipcode",
            "price",
            "sq_ft",
            "rooms",
            "beds",
            "baths",
            "unit_type",
            "neighborhood",
            "borough",
            "broker_fee",
            "central_air_conditioning",
            "dishwasher",
            "doorman",
            "elevator",
            "furnished",
            "parking_available",
            "washer_dryer_in_unit",
            "Availability_Date",
            "photo",
            "latitude",
            "longitude",
        ]
        widgets = {"Availability_Date": forms.DateInput(attrs={"type": "date"})}

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise ValidationError("Price cannot be negative.")
        return price

    def clean_brokerfee(self):
        broker_fee = self.cleaned_data["broker_fee"]
        if broker_fee < 0:
            raise ValidationError("Broker Fee cannot be negative.")
        return broker_fee

    def clean_Availability_Date(self):
        availability_date = self.cleaned_data.get("Availability_Date")
        if availability_date and availability_date < date.today():
            raise ValidationError("The availability date cannot be in the past.")
        if availability_date and availability_date > date.today() + timedelta(days=365):
            raise ValidationError("The availability date is too far in the future.")
        return availability_date

    def clean_rooms_beds(self):
        rooms = self.cleaned_data.get("rooms")
        beds = self.cleaned_data.get("beds")

        if rooms is not None and beds is not None and rooms < beds:
            raise ValidationError(
                "Total number of rooms cannot be less than the number of bedrooms."
            )

    def clean_zipcode(self):
        zipcode = self.cleaned_data["zipcode"]
        if not zipcode.isdigit() or len(zipcode) != 5:
            raise forms.ValidationError("Please enter a valid 5-digit zip code.")
        return zipcode

    def clean_sq_ft(self):
        sq_ft = self.cleaned_data["sq_ft"]
        if sq_ft < 100:
            raise forms.ValidationError(
                "Please enter a valid square footage (100 sq ft minimum)."
            )
        return sq_ft

    def clean_address(self):
        address = self.cleaned_data["address"]
        if len(address) > 255:
            raise forms.ValidationError("Address is too long.")
        return address


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("full_name", "phone_number", "city")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"]
        if not re.match("^[a-zA-Z\\s]*$", full_name):  # noqa: W605
            raise ValidationError("Name should only contain letters and spaces.")
        return full_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise ValidationError("Phone number must contain exactly 10 digits.")
        return phone_number

    def clean_city(self):
        city = self.cleaned_data["city"]
        if not re.match("^[a-zA-Z\\s]*$", city):  # noqa: W605
            raise ValidationError("City should only contain letters and spaces.")
        return city
