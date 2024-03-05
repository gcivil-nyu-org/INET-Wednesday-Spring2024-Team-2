from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER = "user"
    LANDLORD = "landlord"
    USER_TYPES = [
        (USER, "User"),
        (LANDLORD, "Landlord"),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default=USER)
