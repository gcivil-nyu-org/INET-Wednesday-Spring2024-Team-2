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
    s3_doclink = models.CharField(
        max_length=255, blank=True, null=True
    )  # Link to S3 document

    def save(self, *args, **kwargs):
        if self.user_type == CustomUser.USER:
            self.verified = True
        else:
            self.verified = False
        super().save(*args, **kwargs)
