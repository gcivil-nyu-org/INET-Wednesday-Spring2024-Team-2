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
