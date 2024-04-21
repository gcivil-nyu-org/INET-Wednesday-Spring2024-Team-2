from django.test import TestCase, SimpleTestCase, Client, RequestFactory
from django.urls import reverse

from .forms import User, UserSignUpForm, LandlordSignupForm, RentalListingForm
from .models import CustomUser, Rental_Listings, Favorite
from django.contrib.messages import get_messages
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from .views import landlord_profile_update, map_view, profile_view_edit, \
    apply_filters
from .forms import User, UserSignUpForm
from .models import CustomUser, Rental_Listings
from .views import map_view


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

    # def test_listing_detail_view(self):
    #     response = self.client.get(
    #         reverse("listing_detail", kwargs={"listing_id": self.listing.pk})
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, self.listing.address)
    #     self.assertContains(response, self.listing.beds)
    #     self.assertContains(response, self.listing.baths)

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


# class MapViewTestCase(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

# def test_map_view_with_valid_filter_params(self):
#     # Create some Rental_Listings objects for testing
#     # Replace this with appropriate creation of Rental_Listings objects
#     rental_listing_1 = Rental_Listings.objects.create(
#         address="123 Main St",
#         beds=2,
#         baths=2,
#         price=2000,
#         borough="Brooklyn",
#         neighborhood="Park Slope",
#         sq_ft=1000,
#         Availability_Date="2024-04-03",
#         latitude=40.1234,
#         longitude=-73.5678,
#     )
#     rental_listing_2 = Rental_Listings.objects.create(
#         address="456 Main St",
#         beds=1,
#         baths=1,
#         price=4000,
#         borough="Manhattan",
#         neighborhood="Murray Hill",
#         sq_ft=1500,
#         Availability_Date="2024-04-03",
#         latitude=40.6996587,
#         longitude=-73.9294536,
#     )

#     # Prepare a request with valid filter_params
#     request = self.factory.get(
#         "/map/",
#         {
#             "filter_params": '{"borough": "Manhattan", "min_price": "", "max_price": ""}'
#         },
#     )

#     # Call the view function
#     response = map_view(request)

#     # Check if the response status code is 200
#     self.assertEqual(response.status_code, 200)


# class ProfileViewEditTestCase(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = CustomUser.objects.create_user(
#             username='testuser', email='test@example.com', user_type='user' , phone_number = 9876543210, city = 'New York'
#         )

#     def test_profile_view_edit_get(self):
#         url = reverse('profile_view_edit')
#         request = self.factory.get(url)
#         request.user = self.user
#         response = profile_view_edit(request)
#         self.assertEqual(response.status_code, 200)

#     def test_profile_view_edit_post(self):
#         url = reverse('profile_view_edit')
#         data = {'full_name': 'Test User', 'phone_number' :  9876543211, 'city': 'Brooklyn' }
#         request = self.factory.post(url, data)
#         request.user = self.user
#         response = profile_view_edit(request)
#         self.assertEqual(response.status_code, 200)  # Check for redirect after successful form submission

#         updated_user = CustomUser.objects.get(pk=self.user.pk)
#         self.assertEqual(updated_user.full_name, 'Test User')


# class LandlordProfileUpdateTestCase(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = CustomUser.objects.create_user(
#             username='testlandlord', email='landlord@example.com', user_type='landlord', phone_number = 9876543210, city = 'New York'
#         )

#     def test_landlord_profile_update_get(self):
#         url = reverse('landlord_profile_update')
#         request = self.factory.get(url)
#         request.user = self.user
#         response = landlord_profile_update(request)
#         self.assertEqual(response.status_code, 200)

#     def test_landlord_profile_update_post(self):
#         url = reverse('landlord_profile_update')
#         data = {'full_name': 'Test Landlord',  'phone_number'  : 9876543211, 'city' : 'New York'}
#         request = self.factory.post(url, data)
#         request.user = self.user
#         response = landlord_profile_update(request)
#         self.assertEqual(response.status_code, 200)  # Check for redirect after successful form submission

#         updated_user = CustomUser.objects.get(pk=self.user.pk)
#         self.assertEqual(updated_user.full_name, 'Test Landlord')


class ProfileUpdateTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            user_type="user",
        )
        self.client.login(username="testuser", password="testpassword123")

    def test_profile_update_form_loads_correctly(self):
        """Test that the profile update form loads with the correct initial data."""
        response = self.client.get(reverse("profile_view_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'value="test@example.com"'
        )  # Check for pre-filled email
        self.assertContains(
            response, 'value="testuser"'
        )  # Check for pre-filled username

    def test_unauthenticated_access_redirects_to_login(self):
        """Test that unauthenticated users are redirected to the login page."""
        self.client.logout()  # Log out to test unauthenticated access
        response = self.client.get(reverse("profile_view_edit"))
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('profile_view_edit')}"
        )

    def test_successful_profile_update(self):
        """Test submitting the form with valid data updates the user's profile."""
        data = {
            "full_name": "Test User",
            "phone_number": 9876543211,
            "city": "New York",
        }
        response = self.client.post(reverse("profile_view_edit"), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Test User")
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Your profile was successfully updated!", messages)

    def test_invalid_form_submission(self):
        """Test that invalid form submissions are handled correctly."""
        data = {
            "full_name": "",
        }
        response = self.client.post(reverse("profile_view_edit"), data)
        self.assertEqual(response.status_code, 200)  # Page reloads with form errors
        self.assertFormError(response, "form", "full_name", "This field is required.")


class LandlordProfileUpdateTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username="testlandlord",
            email="test@example.com",
            password="testpassword123",
            user_type="landlord",
        )
        self.client.login(username="testlandlord", password="testpassword123")

    def test_profile_update_form_loads_correctly(self):
        """Test that the profile update form loads with the correct initial data."""
        response = self.client.get(reverse("landlord_profile_update"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'value="test@example.com"'
        )  # Check for pre-filled email
        self.assertContains(
            response, 'value="testlandlord"'
        )  # Check for pre-filled username

    def test_unauthenticated_access_redirects_to_login(self):
        """Test that unauthenticated users are redirected to the login page."""
        self.client.logout()  # Log out to test unauthenticated access
        response = self.client.get(reverse("landlord_profile_update"))
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('landlord_profile_update')}"
        )

    def test_successful_profile_update(self):
        """Test submitting the form with valid data updates the user's profile."""
        data = {
            "full_name": "Test Landlord",
            "phone_number": 9876543211,
            "city": "New York",
        }
        response = self.client.post(reverse("landlord_profile_update"), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Test Landlord")
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Your profile was successfully updated!", messages)

    def test_invalid_form_submission(self):
        """Test that invalid form submissions are handled correctly."""
        data = {
            "full_name": "",
        }
        response = self.client.post(reverse("landlord_profile_update"), data)
        self.assertEqual(response.status_code, 200)  # Page reloads with form errors
        self.assertFormError(response, "form", "full_name", "This field is required.")

class RentalListingsFormTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@nyu.edu", password="testpass123"
        )

        self.common_data = {
            'address': "123 Main St",
            'zipcode': "10001",
            'price': 1500,
            'sq_ft': 500,
            'rooms': 3,
            'beds': 2,
            'baths': 1,
            'unit_type': "Apartment",
            'neighborhood': "Midtown",
            'borough': "Manhattan",
            'Submitted_date': date.today(),
        }



    def test_form_with_negative_price(self):
        data = self.common_data.copy()
        data['price'] = -100
        form = RentalListingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertEqual(form.errors['price'], ['Price cannot be negative.'])

    def test_form_with_invalid_zipcode(self):
        data = self.common_data.copy()
        data['zipcode'] = '123'
        form = RentalListingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('zipcode', form.errors)
        self.assertEqual(form.errors['zipcode'], ['Please enter a valid 5-digit zip code.'])

    def test_form_with_invalid_availability_date(self):
        data = self.common_data.copy()
        data['Availability_Date'] = date.today() - timedelta(days=1)
        form = RentalListingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('Availability_Date', form.errors)
        self.assertEqual(form.errors['Availability_Date'], ['The availability date cannot be in the past.'])

    def test_form_with_rooms_less_than_beds(self):
        data = self.common_data.copy()
        data['rooms'] = 1
        data['beds'] = 2
        form = RentalListingForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_with_large_address(self):
        data = self.common_data.copy()
        data['address'] = 'x' * 256
        form = RentalListingForm(data=data)
        self.assertFalse(form.is_valid())


class TestApplyFilters(TestCase):
    def setUp(self):
        # Creating test listings
        self.listing1 = Rental_Listings.objects.create(
            neighborhood='Manhattan', borough='Manhattan', price=2000,
            beds=2, baths=1, elevator=True, washer_dryer_in_unit=False,
            broker_fee=0, unit_type='Apartment', address='123 Main Street'
        )
        self.listing2 = Rental_Listings.objects.create(
            neighborhood='Brooklyn', borough='Brooklyn', price=1500,
            beds=1, baths=1, elevator=False, washer_dryer_in_unit=True,
            broker_fee=500, unit_type='House', address='124 Main Street'
        )
        self.listing3 = Rental_Listings.objects.create(
            neighborhood='Queens', borough='Queens', price=1000,
            beds=3, baths=2, elevator=True, washer_dryer_in_unit=True,
            broker_fee=300, unit_type='Apartment', address='125 Main Street'
        )

    def test_filter_by_borough(self):
        filter_params = {'borough': 'Manhattan'}
        filtered_listings = apply_filters(Rental_Listings.objects.all(), filter_params)
        self.assertTrue(self.listing1 in filtered_listings)
        self.assertFalse(self.listing2 in filtered_listings)
        self.assertFalse(self.listing3 in filtered_listings)

    def test_filter_by_price_range(self):
        filter_params = {'min_price': 1200, 'max_price': 2500}
        filtered_listings = apply_filters(Rental_Listings.objects.all(), filter_params)
        self.assertTrue(self.listing1 in filtered_listings)
        self.assertTrue(self.listing2 in filtered_listings)
        self.assertFalse(self.listing3 in filtered_listings)

    def test_filter_by_bedrooms(self):
        filter_params = {'bedrooms': '2'}
        filtered_listings = apply_filters(Rental_Listings.objects.all(), filter_params)
        self.assertTrue(self.listing1 in filtered_listings)
        self.assertFalse(self.listing2 in filtered_listings)

    def test_filter_by_elevator(self):
        filter_params = {'elevator': True}
        filtered_listings = apply_filters(Rental_Listings.objects.all(), filter_params)
        self.assertTrue(self.listing1 in filtered_listings)
        self.assertFalse(self.listing2 in filtered_listings)
        self.assertTrue(self.listing3 in filtered_listings)

    def test_no_filters(self):
        filter_params = {}
        filtered_listings = apply_filters(Rental_Listings.objects.all(), filter_params)
        self.assertEqual(len(filtered_listings), 3)  # Should return all listings

