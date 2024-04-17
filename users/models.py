from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER = "user"
    LANDLORD = "landlord"
    USER_TYPES = [
        (USER, "User"),
        (LANDLORD, "Landlord"),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default=USER)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    verified = models.BooleanField(default=True)
    s3_doclink = models.CharField(max_length=255, blank=True, null=True)

    # user_type = models.CharField(max_length=20, choices=USER_TYPES, default=LANDLORD)
    # city = models.CharField(max_length=100)
    # full_name = models.CharField(max_length=100)
    # phone_number = models.CharField(max_length=100)
    # email = models.CharField(max_length=100)
    # verified = models.CharField(max_length=100, default="false")
    # s3_doclink = models.URLField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.user_type == CustomUser.USER:
            self.verified = True
        else:
            self.verified = False
        super().save(*args, **kwargs)


class Rental_Listings(models.Model):
    address = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    link = models.URLField(max_length=2048, blank=True, null=True)
    sq_ft = models.IntegerField(blank=True, null=True)
    rooms = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    beds = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    baths = models.DecimalField(max_digits=3, decimal_places=1)
    unit_type = models.CharField(max_length=100, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    central_air_conditioning = models.BooleanField(default=False)
    dishwasher = models.BooleanField(default=False)
    doorman = models.BooleanField(default=False)
    elevator = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    parking_available = models.BooleanField(default=False)
    washer_dryer_in_unit = models.BooleanField(default=False)
    A = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    C = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    E = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    B = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    D = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    F = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    M = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    G = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    L = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    J = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    Z = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    N = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    Q = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    R = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    one = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    two = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    three = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    four = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    five = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    six = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    seven = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    borough = models.CharField(max_length=100, blank=True, null=True)
    broker_fee = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    Landlord = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="rental_listings",
        null=True,
        blank=True,
    )
    Submitted_date = models.DateField(blank=True, default="2024-01-03")
    Availability_Date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.address


class UsersHpdData(models.Model):
    hpd = models.OneToOneField(
        Rental_Listings,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="hpd_data",
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    most_recent_violation_date = models.DateField(blank=True, null=True)
    count_violations = models.BigIntegerField(blank=True, null=True)
    num_complaints = models.BigIntegerField(blank=True, null=True)
    num_noise_complaints = models.BigIntegerField(blank=True, null=True)
    most_recent_complaint = models.DateTimeField(blank=True, null=True)
    ttl_infested_apartments = models.DecimalField(
        max_digits=36, decimal_places=0, blank=True, null=True
    )
    last_bedbug_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users_hpd_data"

    def __str__(self):
        return self.address


class ExampleTable(models.Model):
    example_column = models.CharField(max_length=255)

    def __str__(self):
        return self.example_column


class RentalImages(models.Model):
    rental_listing = models.ForeignKey(
        Rental_Listings, on_delete=models.CASCADE, related_name="images"
    )
    image_url = models.URLField(max_length=2048)

    def __str__(self):
        return self.image_url


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="favorites"
    )
    listing = models.ForeignKey(
        Rental_Listings, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "listing")

    def _str_(self):
        return f"{self.user.username} - {self.listing.address}"


class BuildingInfestationReport(models.Model):
    building_id = models.IntegerField()
    registration_id = models.IntegerField()
    borough = models.CharField(max_length=100)
    house_number = models.CharField(max_length=50)
    street_name = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255)
    dwelling_units = models.CharField(max_length=255)
    infested_dwelling_unit_count = models.CharField(max_length=255)
    eradicated_unit_count = models.CharField(max_length=255)
    reinfested_dwelling_unit_count = models.CharField(max_length=255)
    filing_date = models.DateField()
    filing_period_start_date = models.DateField()
    filing_period_end_date = models.DateField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    community_board = models.CharField(max_length=255)
    council_district = models.CharField(max_length=255)
    census_tract = models.CharField(max_length=50)
    bin = models.CharField(max_length=255)
    bbl = models.CharField(max_length=255)
    nta = models.CharField(max_length=255)

    def _str_(self):
        return f"{self.building_id} - {self.street_name}"


class ExampleTable1(models.Model):
    example_column = models.CharField(max_length=255)

    def _str_(self):
        return self.example_column


class BuildingViolation(models.Model):
    violation_id = models.IntegerField(unique=True)
    building_id = models.IntegerField(default=0)
    registration_id = models.CharField(max_length=100, default="")
    boro_id = models.CharField(max_length=100, default="")
    borough = models.CharField(max_length=100, default="")
    house_number = models.CharField(max_length=50, default="")
    low_house_number = models.CharField(max_length=50, default="")
    high_house_number = models.CharField(max_length=50, default="")
    street_name = models.CharField(max_length=255, default="")
    street_code = models.CharField(max_length=100, default="")
    postcode = models.CharField(max_length=100, default="")
    apartment = models.CharField(max_length=100, default="")
    story = models.CharField(max_length=100, default="")
    block = models.CharField(max_length=100, default="")
    # lot = models.CharField(max_length=100, default='')
    # Class = models.CharField(max_length=100, default='')
    inspection_date = models.DateField(default="2000-01-01")
    approved_date = models.DateField(default="2000-01-01")
    originalcertifybydate = models.DateField(default="2000-01-01")
    originalcorrectbydate = models.DateField(default="2000-01-01")
    # newcertifybydate = models.DateField(default='2000-01-01')
    # newcorrectbydate = models.DateField(default='2000-01-01')
    # certifieddate = models.DateField(default='2000-01-01')
    ordernumber = models.CharField(max_length=100, default="")
    nov_id = models.CharField(max_length=100, default="")
    # nov_description = models.TextField(default='')
    nov_issued_date = models.DateField(default="2000-01-01")
    current_status_id = models.CharField(max_length=100, default="")
    current_status = models.CharField(max_length=100, default="")
    # current_status_date = models.DateField(default='2000-01-01')
    # nov_type = models.CharField(max_length=100, default='')
    # violation_status = models.CharField(max_length=50, default='')
    # rent_impairing = models.CharField(max_length=1, default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    community_board = models.CharField(max_length=100, default="")
    council_district = models.CharField(max_length=100, default="")
    census_tract = models.CharField(max_length=100, default="")
    bin = models.CharField(max_length=100, default="")
    bbl = models.CharField(max_length=20, default="")
    # nta = models.CharField(max_length=100, default='')

    def str(self):
        return f"{self.violation_id} - {self.borough} - {self.street_name}"


class ExampleTable3(models.Model):
    example_column = models.CharField(max_length=255)

    def str(self):
        return self.example_column


class ServiceReport311(models.Model):
    unique_key = models.BigIntegerField(unique=True)
    created_date = models.DateTimeField()
    closed_date = models.DateTimeField(blank=True, null=True)
    agency = models.CharField(max_length=50)
    complaint_type = models.CharField(max_length=255)
    incident_zip = models.CharField(max_length=20, blank=True, null=True)
    incident_address = models.CharField(max_length=255, blank=True, null=True)
    street_name = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50)
    due_date = models.DateTimeField(blank=True, null=True)
    resolution_action_updated_date = models.DateTimeField(blank=True, null=True)
    community_board = models.CharField(max_length=50)
    borough = models.CharField(max_length=100)
    park_borough = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def _str_(self):
        return f"{self.complaint_type} at {self.incident_address} ({self.borough})"
