from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import User, UserSignUpForm
from .models import CustomUser, Rental_Listings, RentalImages
from django.contrib.messages import get_messages

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


class LoginProcessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user and a landlord for testing login
        cls.user = CustomUser.objects.create_user(
            username="testuser", password="testpassword", user_type=CustomUser.USER
        )
        cls.landlord = CustomUser.objects.create_user(
            username="testlandlord",
            password="testpassword",
            user_type=CustomUser.LANDLORD,
            verified=True,
        )
        cls.landlord.save()

    def test_user_login_success(self):
        response = self.client.post(
            reverse("user_login"), {"username": "testuser", "password": "testpassword"}
        )
        self.assertRedirects(response, reverse("user_homepage"))




class LogoutViewTest(TestCase):
    def test_logout_redirect(self):
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, "/")


class Custom404HandlerTest(TestCase):
    def test_redirect_for_authenticated_landlord(self):
        landlord = CustomUser.objects.create_user(
            username="landlord404", password="password", user_type=CustomUser.LANDLORD
        )
        self.client.login(username="landlord404", password="password")
        self.assertIsNotNone(landlord.id)
        response = self.client.get("/nonexistentpage")
        self.assertRedirects(response, reverse("landlord_homepage"))

    def test_redirect_for_authenticated_user(self):
        user = CustomUser.objects.create_user(
            username="user404", password="password", user_type=CustomUser.USER
        )
        self.client.login(username="user404", password="password")
        self.assertIsNotNone(user.id)
        response = self.client.get("/nonexistentpage")
        self.assertRedirects(response, reverse("user_homepage"))

    def test_redirect_for_unauthenticated_user(self):
        response = self.client.get("/nonexistentpage")
        self.assertRedirects(response, reverse("index"))


class LandlordSignUpTest(TestCase):
    def test_landlord_signup_form_display_on_get_request(self):
        response = self.client.get(reverse("landlord_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup/landlord_signup.html")

    def test_landlord_signup_success_on_valid_post_request(self):
        form_data = {
            "username": "landlorduser",
            "email": "landlord@nyu.edu",
            "full_name": "Landlord User",
            "phone_number": "0987654321",
            "city": "Landlord City",
            "password1": "landlordpassword123",
            "password2": "landlordpassword123",
            # Assume "pdf_file" is optional for simplicity; otherwise,
            # use SimpleUploadedFile for tests
        }
        response = self.client.post(reverse("landlord_signup"), form_data)
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.LANDLORD).count(), 1
        )
        self.assertRedirects(response, reverse("landlord_login"))

    def test_landlord_signup_error_on_invalid_post_request(self):
        form_data = {
            "username": "landlorduser",
            "email": "landlorduser@nyu.edu",
            # Missing fields
            "password1": "landlordpassword123",
            "password2": "landlordpassword123",
        }
        response = self.client.post(reverse("landlord_signup"), form_data)
        self.assertEqual(CustomUser.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)


class AddRentalListingTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.landlord_user = CustomUser.objects.create_user(
            username='testlandlord',
            email='landlord@example.com',
            password='testpassword123',
            user_type=CustomUser.LANDLORD
        )

    def test_rental_listing_form_display_on_get_request(self):
        self.client.login(username='testlandlord', password='testpassword123')
        response = self.client.get(reverse("post_new_listings"))
        self.assertEqual(response.status_code, 200)



    def test_rental_listing_error_on_invalid_post_request(self):
        self.client.login(username='testlandlord', password='testpassword123')
        form_data = {
        }
        response = self.client.post(reverse("post_new_listings"), form_data)
        self.assertEqual(Rental_Listings.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)

class RentalListingsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('testuser', 'test@example.com', 'password')
        Rental_Listings.objects.create(address='123 Test St', price=1000, borough='Manhattan', beds='2', baths='1', elevator=True, washer_dryer_in_unit=False, broker_fee=0, unit_type='Apartment', parking_available=True)
        Rental_Listings.objects.create(address='456 Test Ave', price=2000, borough='Brooklyn', beds='3', baths='2', elevator=False, washer_dryer_in_unit=True, broker_fee=0, unit_type='Condo', parking_available=False)
        self.client.login(username='testuser', password='password')


    def test_rentals_page_response_and_filters(self):
        response = self.client.get(reverse('rentalspage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/searchRental/rentalspage.html')
        response = self.client.get(reverse('rentalspage') + '?borough=Manhattan&min_price=500&max_price=1500')
        listings = response.context['page_obj']

    def test_rentals_page_pagination(self):
        response = self.client.get(reverse('rentalspage') + '?page=2')

