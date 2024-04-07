from django.test import TestCase, SimpleTestCase, Client
from django.urls import reverse

from .forms import User, UserSignUpForm, LandlordSignupForm
from .models import CustomUser, Rental_Listings, Favorite
from django.contrib.messages import get_messages
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock


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

    def test_unverified_landlord_login_attempt(self):
        # Make sure this landlord is not verified for this test case.
        unverified_landlord = CustomUser.objects.create_user(
            username="unverified_landlord",
            password="testpassword",
            user_type=CustomUser.LANDLORD,
            verified=False,
        )
        self.assertIsNotNone(unverified_landlord.id)
        response = self.client.post(
            reverse("landlord_login"),
            {"username": "unverified_landlord", "password": "testpassword"},
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Your account has not been verified by the admin yet."
                in message.message
                for message in messages
            )
        )


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


class UserSignUpFormTest(TestCase):
    def test_invalid_email_domain(self):
        form_data = {
            "email": "user@example.com",  # Invalid email domain
            "full_name": "Test User",
            "phone_number": "1234567890",
            "city": "New York",
            "password1": "strongpassword",
            "password2": "strongpassword",
        }
        form = UserSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class CustomUserModelStrTest(TestCase):
    def test_custom_user_str(self):
        user = CustomUser.objects.create_user(
            username="testuser", email="testuser@nyu.edu"
        )
        self.assertEqual(str(user), "testuser")


class LandingPageViewTest(TestCase):
    def test_landing_page_status_code(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)


class LogoutTest(TestCase):
    def test_logout_functionality(self):
        user = CustomUser.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)


class UserAccessTest(TestCase):
    def test_protected_view_access(self):
        response = self.client.get(reverse("user_homepage"))
        self.assertEqual(response.status_code, 302)  # Redirect to login page


class PasswordResetViewTest(TestCase):
    def test_password_reset_page(self):
        response = self.client.get(reverse("password_reset_form"))
        self.assertEqual(response.status_code, 200)


# class RentalsPageViewTest(TestCase):
#     def test_rentals_page_view(self):
#         response = self.client.get(reverse('rentalspage'))
#         self.assertEqual(response.status_code, 302)
#         self.assertTemplateUsed(response, 'users/searchRental/rentalspage.html')


class RentalListingsModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@nyu.edu", password="testpass123"
        )

    # def test_rental_listing_creation(self):
    #     listing = Rental_Listings.objects.create(
    #         address='123 Test St',
    #         price=2000.00,
    #         Landlord=self.user,
    #         Submitted_date=date.today()
    #     )
    #     self.assertEqual(Rental_Listings.objects.count(), 1)
    #     self.assertEqual(listing.address, '123 Test St')
    #     self.assertEqual(listing.Landlord, self.user)


class UserSignUpFormTests(TestCase):
    def test_clean_email_valid(self):
        form_data = {
            "username": "valid@nyu.edu",
            "email": "valid@nyu.edu",
            "password1": "testpassword",
            "password2": "testpassword",
            "full_name": "Valid User",
            "phone_number": "1234567890",
            "city": "New York",
        }
        form = UserSignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_email_invalid_domain(self):
        form_data = {
            "username": "invalid@gmail.com",
            "email": "invalid@gmail.com",
            "password1": "testpassword",
            "password2": "testpassword",
            "full_name": "Invalid User",
            "phone_number": "1234567890",
            "city": "New York",
        }
        form = UserSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class LandlordSignupFormTests(TestCase):
    def test_form_save(self):
        form_data = {
            "username": "landlord@nyu.edu",
            "email": "landlord@nyu.edu",
            "password1": "landlordpassword",
            "password2": "landlordpassword",
            "full_name": "Landlord User",
            "phone_number": "9876543210",
            "city": "New York",
        }
        form = LandlordSignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        landlord = form.save()
        self.assertEqual(landlord.email, "landlord@nyu.edu")
        self.assertEqual(landlord.user_type, CustomUser.LANDLORD)


class FavoriteModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="favuser", email="favuser@nyu.edu", password="testpass123"
        )
        self.listing = Rental_Listings.objects.create(
            address="123 Fav St", price=1500.00, baths=1, Landlord=self.user
        )

    def test_favorite_creation(self):
        favorite = Favorite.objects.create(user=self.user, listing=self.listing)
        self.assertEqual(Favorite.objects.count(), 1)
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.listing, self.listing)


class LogoutViewTests(TestCase):
    def test_logout(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, "/")


class HomeViewTests(TestCase):
    def test_home_view_status_code(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)


# class UserHomeViewTests(TestCase):
#     def test_user_home_redirect_for_anonymous(self):
#         response = self.client.get(reverse('user_homepage'), follow=True)
#         self.assertRedirects(response, '/login/user_login?next=/user/home/')

# class LandlordHomeViewTests(TestCase):
#     def test_landlord_home_redirect_for_anonymous(self):
#         response = self.client.get(reverse('landlord_homepage'), follow=True)
#         self.assertRedirects(response, '/login/landlord_login?next=/landlord/home/')


class RentalsPageViewTests(TestCase):
    def test_rentals_page_for_user(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("rentalspage"))
        self.assertEqual(response.status_code, 302)


# class FavoritesPageViewTests(TestCase):
#     def test_favorites_page_for_user(self):
#         self.client.login(username='testuser', password='testpass123')  # Make sure the user is logged in
#         response = self.client.get(reverse('favorites_page'))
#         self.assertEqual(response.status_code, 200)


class UserSignUpViewTests(TestCase):
    def test_user_signup_with_invalid_data(self):
        response = self.client.post(reverse("user_signup"), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


class LandlordSignUpViewTests(TestCase):
    def test_landlord_signup_with_valid_data(self):
        form_data = {
            "username": "newlandlord",
            "email": "newlandlord@nyu.edu",
            "password1": "landlordpassword123",
            "password2": "landlordpassword123",
            "full_name": "New Landlord",
            "phone_number": "1234567890",
            "city": "New York City",
        }
        response = self.client.post(reverse("landlord_signup"), form_data)
        self.assertRedirects(response, reverse("landlord_login"))
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.LANDLORD).count(), 1
        )


class UserLoginViewTests(TestCase):
    def test_user_login_redirect(self):
        user = CustomUser.objects.create_user(
            username="loginuser", email="loginuser@nyu.edu", password="password"
        )
        response = self.client.post(
            reverse("user_login"), {"username": "loginuser", "password": "password"}
        )
        self.assertRedirects(response, reverse("user_homepage"))


# class UserHomePageViewTests(TestCase):
#     def test_user_homepage_access_unauthenticated(self):
#         response = self.client.get(reverse("user_homepage"))
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(reverse("user_login") in response.url)


class UserHomePageAuthenticatedAccessTests(TestCase):
    def test_user_homepage_access_authenticated(self):
        user = CustomUser.objects.create_user(
            username="testuserhome", email="testuserhome@nyu.edu", password="password"
        )
        self.client.login(username="testuserhome", password="password")
        response = self.client.get(reverse("user_homepage"))
        self.assertEqual(response.status_code, 200)


class LogoutFunctionalityTests(TestCase):
    def test_logout_redirects_to_home(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("index"))


class RentalListingsAccessTests(TestCase):
    def test_rental_listings_access_by_authenticated_user(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("rentalspage"))
        self.assertEqual(response.status_code, 302)


class LandlordSignupWithFileTest(TestCase):
    @patch("users.views.boto3.client")
    def test_landlord_signup_with_file(self, mock_boto3_client):
        mock_s3_client = mock_boto3_client.return_value
        mock_s3_client.upload_fileobj.return_value = None  # Simulate successful upload

        form_data = {
            "username": "landlordfile@nyu.edu",
            "email": "landlordfile@nyu.edu",
            "password1": "landlordpassword",
            "password2": "landlordpassword",
            "full_name": "Landlord File",
            "phone_number": "9876543210",
            "city": "New York",
            "pdf_file": SimpleUploadedFile(
                "test_file.pdf",
                b"These are the file contents.",
                content_type="application/pdf",
            ),
        }
        response = self.client.post(reverse("landlord_signup"), form_data)
        self.assertRedirects(response, reverse("landlord_login"))
        self.assertTrue(
            CustomUser.objects.filter(email="landlordfile@nyu.edu").exists()
        )


class UserLoginRedirectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuserredirect",
            email="userredirect@nyu.edu",
            password="password123",
            user_type=CustomUser.USER,
        )

    def test_user_login_redirect_to_user_homepage(self):
        self.client.login(username="testuserredirect", password="password123")
        response = self.client.get(reverse("user_homepage"))
        self.assertEqual(response.status_code, 200)


class Custom404HandlerTest(TestCase):
    def test_404_redirect_for_anonymous_user(self):
        response = self.client.get("/thispagedoesnotexist")
        self.assertRedirects(response, reverse("index"))

    def test_404_redirect_for_authenticated_user(self):
        user = CustomUser.objects.create_user(
            username="user404test", password="password"
        )
        self.client.login(username="user404test", password="password")
        response = self.client.get("/thispagedoesnotexist")
        self.assertRedirects(response, reverse("user_homepage"))


class ToggleFavoriteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="favuser",
            email="favuser@nyu.edu",
            password="testpass123",
            user_type=CustomUser.USER,
        )
        cls.listing = Rental_Listings.objects.create(
            address="123 Fav St", price=1500.00, baths=1, Landlord=cls.user
        )

    # def test_toggle_favorite_add(self):
    #     self.client.login(username='favuser', password='testpass123')
    #     response = self.client.post(reverse('toggle_favorite'), json.dumps({'listing_id': self.listing.id}), content_type='application/json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertTrue(Favorite.objects.filter(user=self.user, listing=self.listing).exists())


class LandlordUserPageAccessTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.landlord_user = CustomUser.objects.create_user(
            username="landlorduser",
            email="landlorduser@nyu.edu",
            password="testpass123",
            user_type=CustomUser.LANDLORD,
        )
        cls.user = CustomUser.objects.create_user(
            username="normaluser",
            email="normaluser@nyu.edu",
            password="testpass123",
            user_type=CustomUser.USER,
        )

    def test_landlord_accessing_user_page(self):
        self.client.login(username="landlorduser", password="testpass123")
        response = self.client.get(reverse("user_homepage"))
        self.assertNotEqual(response.status_code, 200)

    def test_user_accessing_landlord_page(self):
        self.client.login(username="normaluser", password="testpass123")
        response = self.client.get(reverse("landlord_homepage"))
        self.assertNotEqual(response.status_code, 200)


class ListingDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

        self.listing = Rental_Listings.objects.create(
            address="123 Main St",
            beds=2,
            baths=2,
            price=2000,
            borough="Brooklyn",
            neighborhood="Park Slope",
            sq_ft=1000,
            Availability_Date="2024-04-03",
            latitude=40.1234,
            longitude=-73.5678,
        )

    def test_listing_detail_view(self):
        # Assuming your view name is 'listing_detail'
        response = self.client.get(
            reverse("listing_detail", kwargs={"listing_id": self.listing.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.address)
        self.assertContains(response, self.listing.beds)
        self.assertContains(response, self.listing.baths)

    def test_toggle_favorite_ajax(self):
        response = self.client.post(
            reverse("toggle_favorite"), {"listing_id": self.listing.pk}
        )
        self.assertEqual(response.status_code, 200)

    def test_listing_detail_not_found(self):
        non_existent_listing_id = 99999  # Assuming this ID does not exist
        response = self.client.get(
            reverse("listing_detail", kwargs={"listing_id": non_existent_listing_id})
        )
        self.assertEqual(response.status_code, 302)


# class InitTestCase(TestCase):
#     def test_default_settings(self):
#         # Do not set ENV_NAME or set it to a value other than "prod" or "develop"
#         from rent_wise_nyc import settings
#         # Assert that settings imported from local.py are correctly applied
#         self.assertEqual(settings.ALLOWED_HOSTS, ["127.0.0.1"])


class ManagePyTestCase(unittest.TestCase):
    @patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": "rent_wise_nyc.settings"})
    @patch("django.core.management.execute_from_command_line")
    def test_main_success(self, mock_execute_from_command_line):
        from manage import main

        main()
        mock_execute_from_command_line.assert_called_once_with(sys.argv)

    @patch("django.core.management.execute_from_command_line", side_effect=ImportError)
    def test_main_import_error(self, mock_execute_from_command_line):
        from manage import main

        with self.assertRaises(ImportError):
            main()
