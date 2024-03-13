from django.test import TestCase
from django.urls import reverse

from .forms import User, UserSignUpForm
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


class UserSignUpTest(TestCase):
    def test_user_signup_form_display_on_get_request(self):
        response = self.client.get(reverse("user_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], UserSignUpForm)
        self.assertTemplateUsed(response, "users/signup/signup.html")

    def test_user_signup_success_on_valid_post_request(self):
        form_data = {
            "username": "testuser",
            "email": "testuser@nyu.edu",
            "full_name": "Test User",
            "phone_number": "1234567890",
            "city": "Test City",
            "s3_doclink": "http://example.com/doc",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        response = self.client.post(reverse("user_signup"), form_data)
        self.assertEqual(User.objects.count(), 1)
        self.assertRedirects(response, reverse("user_homepage"))

    def test_user_signup_error_on_invalid_post_request(self):
        form_data = {
            "username": "testuser",
            "email": "invalid-email",
            "full_name": "Test User",
            "phone_number": "1234567890",
            "city": "Test City",
            "password1": "testpassword123",
            "password2": "wrongpassword",
        }
        response = self.client.post(reverse("user_signup"), form_data)
        self.assertEqual(User.objects.count(), 0)
        self.assertFormError(response, "form", "email", "Enter a valid email address.")
