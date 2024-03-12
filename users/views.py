from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import logging
import logging.config
import sys
from django.urls import reverse
from users.decorators import user_type_required
from users.forms import UserSignUpForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

# from .forms import CustomUserCreationForm
from .forms import LandlordSignupForm
import boto3
from django.conf import settings
from .models import CustomUser
from io import BytesIO
from .forms import CustomLoginForm

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
        return render(request, this_page, {'form': form})

    form = CustomLoginForm(request, request.POST)  # Pass the request to the form
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid credentials!")
            return render(request, this_page, {'form': form})

        if getattr(user, "user_type", None) != user_type:
            messages.error(
                request,
                f"Please provide correct credentials to login as {user_type.capitalize()}!", # noqa:<E501>
            )
            return render(request, this_page, {'form': form})
        if user_type == "landlord" and user.verified == False:
            messages.error(
                request,
                "Your account has not been verified by the admin yet. Please wait!!",
            )
            return render(request, this_page, {'form': form})
        login(request, user)
        return redirect(reverse(destination_url_name))

    return render(request, this_page, {'form': form})

def landlord_login(request):
    return login_process(
        request,
        user_type="landlord",
        this_page="login/landlord_login.html",
        destination_url_name="landlord_homepage",
    )

def user_login(request):
    return login_process(
        request,
        user_type="user",
        this_page="login/user_login.html",
        destination_url_name="user_homepage",  # URL pattern name for user's homepage
    )



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
            user.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("user_homepage")
        else:
            messages.error(request, form.errors)
    else:
        form = UserSignUpForm()
    return render(request, "users/signup/signup.html", {"form": form})


def home(request):
    return render(request, "home.html")


def logout_view(request):
    logout(request)
    return redirect("/")


@user_type_required("user")
def user_home(request):
    return render(request, "user_homepage.html")


@user_type_required("landlord")
def landlord_home(request):
    return render(request, "landlord_homepage.html")


def landlord_signup(request):
    if request.method == "POST":
        form = LandlordSignupForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES)
            user = form.save(commit=False)

            # Upload file to S3 if present
            pdf_file = request.FILES.get("pdf_file")
            print(pdf_file)
            if pdf_file:
                print(f"Received file: {pdf_file.name}")  # Debug print
                file_name = f"pdfs/{pdf_file.name}"  # Customize the path as needed
                # s3_client = boto3.client('s3')
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
                            "A file with the same name already exists. Please rename your file and try again.",
                        )
                        return render(
                            request, "signup/landlord_signup.html", {"form": form}
                        )

                    s3_client.upload_fileobj(
                        pdf_file, "landlord-verification-files", file_name
                    )
                    user.s3_doclink = f"https://landlord-verification-files.s3.amazonaws.com/{file_name}"
                    print("File uploaded successfully")
                except Exception as e:
                    print(f"Error uploading file to S3: {e}")
            user.save()

            messages.success(request, "Signup successful. Please log in.")
            return redirect("landlord_login")
        else:
            messages.error(request, "Signup failed. Please correct the errors below.")
    else:
        form = LandlordSignupForm()
    return render(request, "signup/landlord_signup.html", {"form": form})
