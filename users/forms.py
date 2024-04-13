from datetime import date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
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
    ROOMS_CHOICES = [(i, str(i)) for i in range(1, 11)]
    BATHS_CHOICES = [(i * 0.5, str(i * 0.5)) for i in
                     range(2, 21)]

    UNIT_TYPE_CHOICES = [('Apartment', 'Apartment'),
                         ('House', 'House')]
    NEIGHBORHOOD_CHOICES = [
        ('Manhattan', 'Manhattan'),
        ('Brooklyn', 'Brooklyn'),
        ('Upper East Side', 'Upper East Side'),
        ('Upper West Side', 'Upper West Side'),
        ('Midtown', 'Midtown'),
        ('Harlem', 'Harlem'),
        ('Chelsea', 'Chelsea'),
        ('Greenwich Village', 'Greenwich Village'),
        ('Soho', 'Soho'),
        ('East Village', 'East Village'),
        ('Lower East Side', 'Lower East Side'),
        ('Williamsburg', 'Williamsburg'),
        ('Bushwick', 'Bushwick'),
        ('Park Slope', 'Park Slope'),
        ('Brooklyn Heights', 'Brooklyn Heights'),
        ('Red Hook', 'Red Hook'),
        ('Astoria', 'Astoria'),
        ('Long Island City', 'Long Island City'),
        ('Flushing', 'Flushing'),
        ('Jamaica', 'Jamaica'),
        ('Forest Hills', 'Forest Hills'),
        ('Riverdale', 'Riverdale'),
        ('Fordham', 'Fordham'),
        ('Concourse', 'Concourse'),
        ('Throgs Neck', 'Throgs Neck'),
        ('St. George', 'St. George'),
        ('Tottenville', 'Tottenville'),
        ('Stapleton', 'Stapleton'),
    ]

    BOROUGH_CHOICES = [('Manhattan', 'Manhattan'), ('Brooklyn', 'Brooklyn'),
                       ('Queens', 'Queens'), ('Bronx', 'Bronx'),
                       ('Staten Island', 'Staten Island')]

    rooms = forms.ChoiceField(choices=ROOMS_CHOICES)
    beds = forms.ChoiceField(choices=ROOMS_CHOICES)
    baths = forms.ChoiceField(choices=BATHS_CHOICES)
    unit_type = forms.ChoiceField(choices=UNIT_TYPE_CHOICES)
    neighborhood = forms.ChoiceField(choices=NEIGHBORHOOD_CHOICES)
    borough = forms.ChoiceField(choices=BOROUGH_CHOICES)
    photo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(RentalListingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('address', css_class='form-group col-md-6 mb-0'),
                Column('zipcode', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'price',
            'sq_ft',
            Row(
                Column('rooms', css_class='form-group col-md-4 mb-0'),
                Column('beds', css_class='form-group col-md-4 mb-0'),
                Column('baths', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'unit_type',
            'neighborhood',
            'borough',
            'broker_fee',
            'central_air_conditioning',
            'dishwasher',
            'doorman',
            'elevator',
            'furnished',
            'parking_available',
            'washer_dryer_in_unit',
            'Submitted_date',
            'Availability_Date',
            Field('photo', multiple=True),
            Submit('submit', 'Submit', css_class='btn btn-primary')
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
            "Submitted_date",
            "Availability_Date",
            "photo",
        ]
        widgets = {
            "Submitted_date": forms.DateInput(attrs={"type": "date"}),
            "Availability_Date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_Availability_Date(self):
        availability_date = self.cleaned_data.get("Availability_Date")
        if availability_date and availability_date < date.today():
            raise ValidationError(
                "The availability date cannot be in the past.")
        if availability_date and availability_date > date.today() + timedelta(
                days=365):
            raise ValidationError(
                "The availability date is too far in the future.")
        return availability_date

    def clean_rooms_beds(self):

        rooms = self.cleaned_data.get("rooms")
        beds = self.cleaned_data.get("beds")

        if rooms is not None and beds is not None and rooms < beds:
            raise ValidationError(
                "Total number of rooms cannot be less than the number of bedrooms.")

    def clean_zipcode(self):
        zipcode = self.cleaned_data['zipcode']
        if not zipcode.isdigit() or len(zipcode) != 5:
            raise forms.ValidationError(
                "Please enter a valid 5-digit zip code.")
        return zipcode

    def clean_sq_ft(self):
        sq_ft = self.cleaned_data['sq_ft']
        if sq_ft < 100:
            raise forms.ValidationError(
                "Please enter a valid square footage (100 sq ft minimum).")
        return sq_ft

    def clean_address(self):
        address = self.cleaned_data['address']
        if len(address) > 255:
            raise forms.ValidationError("Address is too long.")
        return address




class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
