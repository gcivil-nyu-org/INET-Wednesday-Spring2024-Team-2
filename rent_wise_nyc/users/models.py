from django.db import models
from django.contrib.auth.models import AbstractUser, Permission #, User
from django.contrib.auth.models import Group as AuthGroup

# Create your models here.

# class User(AbstractUser):
#     # https://docs.djangoproject.com/en/4.2/topics/auth/customizing/
#     pass

class CustomUser(AbstractUser):
    USER = 'user'
    LANDLORD = 'landlord'
    USER_TYPES = [
        (USER, 'User'),
        (LANDLORD, 'Landlord'),
    ]
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default=USER)
    # groups = models.ManyToManyField(AuthGroup, verbose_name='groups', blank=True, related_name='custom_user_set', related_query_name='user')
    # user_permissions = models.ManyToManyField(
    #     Permission,
    #     verbose_name='user permissions',
    #     blank=True,
    #     related_name='custom_user_set',
    #     related_query_name='user'
    # )

# class Landlord(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
    