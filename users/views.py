from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import logging
import logging.config
import sys
from django.urls import reverse
from users.decorators import user_type_required
from users.forms import UserSignUpForm
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

        login(request, user)
        # Redirect to the destination URL
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
            user = form.save()
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
