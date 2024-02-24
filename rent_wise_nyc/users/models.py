from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.auth.models import Group as AuthGroup

# Create your models here.
class CustomUser(AbstractUser):
    USER = 'user'
    LANDLORD = 'landlord'
    USER_TYPES = [
        (USER, 'User'),
        (LANDLORD, 'Landlord'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default=USER)
    groups = models.ManyToManyField(AuthGroup, verbose_name='groups', blank=True, related_name='custom_user_set', related_query_name='user')
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='user'
    )
