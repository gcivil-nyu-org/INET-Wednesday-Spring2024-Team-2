import os
import uuid
import ast

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import logging.config
import sys
from django.urls import reverse
from users.decorators import user_type_required
from users.forms import UserSignUpForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db.models import Q, Min
from .forms import LandlordSignupForm
import boto3
from django.conf import settings
from .models import CustomUser, RentalImages
from .forms import CustomLoginForm
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger

from .models import Favorite, Rental_Listings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from urllib.parse import urlencode
from django.http import JsonResponse
from django.core.serializers import serialize
from django.contrib.sites.models import Site
from .forms import CustomUserEditForm
from .decorators import no_cache
from django.views.decorators.csrf import ensure_csrf_cookie


logger = logging.getLogger(__name__)

LOGGING = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

logging.config.dictConfig(LOGGING)


def custom_404_handler(request, exception):
    if request.user.is_authenticated:
        if getattr(request.user, "user_type", None) == "landlord":
            return redirect("landlord_homepage")
        else:
            return redirect("user_homepage")
    else:
        return redirect("index")


def login_process(request, user_type, this_page, destination_url_name):
    if request.method != "POST":
        form = CustomLoginForm()
        return render(request, this_page, {"form": form})

    form = CustomLoginForm(request, request.POST)  # Pass the request to the form
    if form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid credentials!")
            return render(request, this_page, {"form": form})

        if getattr(user, "user_type", None) != user_type:
            messages.error(
                request,
                f"Please provide correct credentials to login as {user_type.capitalize()}!",  # noqa:<E501>
            )
            return render(request, this_page, {"form": form})
        if user_type == "landlord" and user.verified is False:
            messages.error(
                request,
                "Your account has not been verified by the admin yet. Please wait!",
            )
            return render(request, this_page, {"form": form})
        login(request, user)
        return redirect(reverse(destination_url_name))

    return render(request, this_page, {"form": form})


@no_cache
def landlord_login(request):
    return login_process(
        request,
        user_type="landlord",
        this_page="login/landlord_login.html",
        destination_url_name="landlord_homepage",
    )


@no_cache
def user_login(request):
    return login_process(
        request,
        user_type="user",
        this_page="login/user_login.html",
        destination_url_name="user_homepage",  # URL pattern name for user's homepage
    )


@no_cache
@ensure_csrf_cookie
def user_signup(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = form.save(commit=False)
            user.username = email
            user.save()
            if user.user_type == user.USER:
                user.verified = True
            else:
                user.verified = False
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("user_homepage")
    else:
        form = UserSignUpForm()
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{error}")

    return render(request, "users/signup/signup.html", {"form": form})


@no_cache
def home(request):
    return render(request, "home.html")


@no_cache
def logout_view(request):
    logout(request)
    return redirect("/")


@no_cache
@user_type_required("user")
def user_home(request):
    return render(request, "user_homepage.html")


@no_cache
@user_type_required("landlord")
def landlord_home(request):
    return render(request, "landlord_homepage.html")


@no_cache
def landlord_signup(request):
    if request.method == "POST":
        form = LandlordSignupForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES)
            user = form.save(commit=False)

            # Upload file to S3 if present check
            pdf_file = request.FILES.get("pdf_file")
            print(pdf_file)
            if pdf_file:
                file_name, file_extension = os.path.splitext(pdf_file.name)
                print(f"Received file: {pdf_file.name}")  # Debug print
                file_name = f"pdfs/{file_name}_{uuid.uuid4()}{file_extension}"
                print(file_name)
                try:
                    s3_client = boto3.client(
                        "s3",
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    )

                    # Check if file already exists in S3 bucket
                    existing_files = s3_client.list_objects_v2(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=file_name
                    )

                    if "Contents" in existing_files:
                        messages.error(
                            request,
                            "A file with the same name already exists."
                            " Please rename your file and try again.",
                        )
                        return render(
                            request, "signup/landlord_signup.html", {"form": form}
                        )

                    s3_client.upload_fileobj(
                        pdf_file, "landlord-verification-files", file_name
                    )
                    user.s3_doclink = (
                        f"https://landlord-verification-files."
                        f"s3.amazonaws.com/{file_name}"
                    )
                    print("File uploaded successfully")
                except Exception as e:
                    print(f"Error uploading file to S3: {e}")
            user.save()

            messages.success(request, "Registration successful. Please log in.")
            return redirect("landlord_login")
        else:
            messages.error(
                request, "Registration failed. Please correct the errors below."
            )
    else:
        form = LandlordSignupForm()
    return render(request, "signup/landlord_signup.html", {"form": form})


@no_cache
def apply_filters(listings, filter_params):
    # TODO: fix in database
    listings = listings.exclude(neighborhood="Hell's Kitchen")
    # Apply filters
    if filter_params.get("borough"):
        borough = filter_params.get("borough")
        if borough == "All(NYC)":
            # No need to filter by borough if "All(NYC)" is selected
            pass
        else:
            # Filter by neighborhood or borough using exact match
            listings = listings.filter(Q(neighborhood=borough) | Q(borough=borough))
    if filter_params.get("min_price"):
        min_price = int(filter_params.get("min_price"))
        listings = listings.filter(price__gte=min_price)
    if filter_params.get("max_price"):
        max_price = int(filter_params.get("max_price"))
        listings = listings.filter(price__lte=max_price)
    if filter_params.get("bedrooms"):
        if filter_params.get("bedrooms") == "Any":
            listings = listings
        else:
            listings = listings.filter(beds=filter_params.get("bedrooms"))
    if filter_params.get("bathrooms"):
        if filter_params.get("bathrooms") == "Any":
            listings = listings
        else:
            listings = listings.filter(baths=filter_params.get("bathrooms"))
    if filter_params.get("elevator"):
        listings = listings.filter(elevator=True)
    if filter_params.get("laundry"):
        listings = listings.filter(washer_dryer_in_unit=True)
    if filter_params.get("no_fee"):
        listings = listings.filter(broker_fee=0)
    if filter_params.get("building_type"):
        if filter_params.get("building_type") == "Any":
            listings = listings
        else:
            listings = listings.filter(unit_type=filter_params.get("building_type"))
    if filter_params.get("parking"):
        listings = listings.filter(parking_available=True)
    if filter_params.get("search_query"):
        query = SearchQuery(filter_params.get("search_query"))
        listings = (
            listings.annotate(
                search=SearchVector("address"),
                rank=SearchRank(SearchVector("address"), query),
            )
            .filter(search=query)
            .order_by("-rank")
        )
    return listings


@no_cache
@user_type_required("user")
def rentals_page(request):
    # Filter parameters
    filter_params = {
        "borough": request.GET.get("borough"),
        "min_price": request.GET.get("min_price"),
        "max_price": request.GET.get("max_price"),
        "bedrooms": request.GET.get("bedrooms"),
        "bathrooms": request.GET.get("bathrooms"),
        "elevator": request.GET.get("elevator") == "on",
        "laundry": request.GET.get("laundry") == "on",
        "no_fee": request.GET.get("no_fee") == "on",
        "building_type": request.GET.get("building_type"),
        "parking": request.GET.get("parking") == "on",
        "search_query": request.GET.get("search_query", ""),
    }

    # Start with all listings
    listings = Rental_Listings.objects.all()

    # Apply filters
    listings = apply_filters(listings, filter_params)

    # Annotate each listing with the URL of its first image
    listings = listings.annotate(first_image=Min("images__image_url"))

    # Sorting
    sort_option = request.GET.get("sort")
    if sort_option == "recent":
        listings = listings.order_by(
            "-Submitted_date"
        )  # Assuming you have a created_at field
    elif sort_option == "high_to_low":
        listings = listings.order_by("-price")
    else:
        listings = listings.order_by("price")

    # Query to get the IDs of listings that are favorited by the current user
    favorite_listings_ids = Favorite.objects.filter(user=request.user).values_list(
        "listing__id", flat=True
    )
    filter_params = {k: v for k, v in filter_params.items() if v is not None}

    # Pagination
    paginator = Paginator(listings, 5)  # Show 5 listings per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Query to get the IDs of listings that are favorited by the current user
    favorite_listings_ids = Favorite.objects.filter(user=request.user).values_list(
        "listing__id", flat=True
    )

    # Pass listings_json and favorite_listings_ids to the template
    context = {
        "page_obj": page_obj,
        "listings": listings,
        "favorite_listings_ids": list(favorite_listings_ids),
        "filter_params": filter_params,  # Ensure it's converted to a list
    }

    return render(request, "users/searchRental/rentalspage.html", context)


@no_cache
@login_required
def placeholder_view(request):
    return render(request, "users/searchRental/placeholder.html")


@no_cache
def listing_detail(request, listing_id):
    # Retrieve the specific listing based on the ID provided in the URL parameter
    listing = get_object_or_404(Rental_Listings, id=listing_id)

    # Pass the listing data to a template for rendering
    context = {"listing": listing}
    return render(request, "users/searchRental/listing_detail.html", context)


@no_cache
@csrf_exempt
@login_required
@user_type_required("user")
def toggle_favorite(request):
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        if not listing_id:
            return JsonResponse({"error": "Listing ID is required"}, status=400)

        try:
            listing = Rental_Listings.objects.get(id=listing_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user, listing=listing
            )
            if not created:
                favorite.delete()
                return JsonResponse({"status": "removed"})
            return JsonResponse({"status": "added"})
        except Rental_Listings.DoesNotExist:
            return JsonResponse({"error": "Listing not found"}, status=404)
        except Exception as e:
            logger.error(f"Internal server error: {e}", exc_info=True)
            return JsonResponse({"error": "Internal server error"}, status=500)


@user_type_required("user")
@login_required
@no_cache
def favorites_page(request):
    # Fetch only the listings that the user has marked as favorite
    favorite_listings = Favorite.objects.filter(user=request.user).select_related(
        "listing"
    )
    listings = [fav.listing for fav in favorite_listings]

    listings_json = serializers.serialize("json", listings)
    favorite_listings_ids = [listing.id for listing in listings]

    context = {
        "listings_json": listings_json,
        "favorite_listings_ids": favorite_listings_ids,
    }
    return render(request, "users/searchRental/favorites.html", context)


@no_cache
def map_view(request):
    # Fetch all rental listings from your model
    filter_params = ast.literal_eval(request.GET.get("filter_params"))
    rental_listings = Rental_Listings.objects.all()

    # http://127.0.0.1:8000/map/?filter_params={%27borough%27:%20%27Manhattan%27,%20%27min_price%27:%20%27%27,%20%27max_price%27:%20%27%27}
    rental_listings = apply_filters(rental_listings, filter_params)

    rental_listings_json = serialize("json", rental_listings)

    current_site = Site.objects.get_current()
    current_site.domain

    # return JsonResponse(rental_listings_json, safe=False)
    context = {
        "rental_listings": rental_listings_json,
        "this_domain": current_site.domain,
    }
    return render(request, "users/searchRental/map_view.html", context)


@login_required
@no_cache
@user_type_required("user")
def profile_view_edit(request):
    if request.method == "POST":
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("profile_view_edit")
    else:
        form = CustomUserEditForm(instance=request.user)

    return render(
        request,
        "users/Profile/profile_view_edit.html",
        {"form": form, "user": request.user},
    )


@login_required
@no_cache
@user_type_required("landlord")
def landlord_profile_update(request):
    if request.method == "POST":
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("landlord_profile_update")
    else:
        form = CustomUserEditForm(instance=request.user)

    return render(
        request,
        "users/Profile/landlord_profile_update.html",
        {"form": form, "user": request.user},
    )
