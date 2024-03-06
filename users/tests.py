from django.test import TestCase
from .models import CustomUser


class CustomUserModelTests(TestCase):
    def test_create_user_with_default_user_type(self):
        user = CustomUser.objects.create_user(username="test_user", password="password")
        self.assertEqual(user.user_type, CustomUser.USER)

    def test_create_user_with_landlord_user_type(self):
        user = CustomUser.objects.create_user(
            username="landlord_user", password="password", user_type=CustomUser.LANDLORD
        )
        self.assertEqual(user.user_type, CustomUser.LANDLORD)

    def test_create_superuser_with_default_user_type(self):
        superuser = CustomUser.objects.create_superuser(
            username="superuser", password="password"
        )
        self.assertEqual(superuser.user_type, CustomUser.USER)

    def test_create_superuser_with_landlord_user_type(self):
        superuser = CustomUser.objects.create_superuser(
            username="superuser", password="password", user_type=CustomUser.LANDLORD
        )
        self.assertEqual(superuser.user_type, CustomUser.LANDLORD)
