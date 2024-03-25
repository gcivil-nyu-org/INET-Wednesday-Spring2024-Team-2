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


class RentalListings(models.Model):
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
    A = models.BooleanField(default=False)
    C = models.BooleanField(default=False)
    E = models.BooleanField(default=False)
    B = models.BooleanField(default=False)
    D = models.BooleanField(default=False)
    F = models.BooleanField(default=False)
    M = models.BooleanField(default=False)
    G = models.BooleanField(default=False)
    L = models.BooleanField(default=False)
    J = models.BooleanField(default=False)
    Z = models.BooleanField(default=False)
    N = models.BooleanField(default=False)
    Q = models.BooleanField(default=False)
    R = models.BooleanField(default=False)
    one = models.BooleanField(default=False)
    two = models.BooleanField(default=False)
    three = models.BooleanField(default=False)
    four = models.BooleanField(default=False)
    five = models.BooleanField(default=False)
    six = models.BooleanField(default=False)
    seven = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    borough = models.CharField(max_length=100, blank=True, null=True)
    broker_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # landlord = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rental_listings', null=True,
    #                              blank=True)

    def _str_(self):
        return self.address
