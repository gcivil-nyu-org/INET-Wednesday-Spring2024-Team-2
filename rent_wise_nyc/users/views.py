from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
import logging, logging.config
import sys

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

logging.config.dictConfig(LOGGING)

def login_process(request, user_type, this_page, destination):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        logging.info(f"logging in as {username}")
        user = authenticate(username=username, password=password)
        logging.info(f"{user.user_type=}")
        if user.user_type == user_type:
            login(request, user)
            logging.info(f"logged in {user=}")
            return render(request, destination)
        else:
            # Return an error message or render the login page again
            messages.error(request,'Invalid credentials!!')
            logging.info("invalid credentials")
            return render(request, this_page, {'error': 'Invalid credentials!'})
    else:
        return render(request, this_page)

def landlord_login(request):
    return login_process(
        request, 
        user_type="landlord", 
        this_page="registration/landlord_login.html", 
        destination="landlord_homepage.html"
    )
    
def user_login(request):
    return login_process(
        request, 
        user_type="user", 
        this_page="registration/user_login.html", 
        destination="user_homepage.html"
    )

def home(request):
    return render(request,"home.html")

def logout_view(request):
    logout(request)
    return redirect("/")

def user_home(request):
    response = "It's the user homepage."
    return HttpResponse(response)

def landlord_home(request):
    logging.info("hello here at landlord page")
    response = "It's the landlord homepage."
    return HttpResponse(response)

