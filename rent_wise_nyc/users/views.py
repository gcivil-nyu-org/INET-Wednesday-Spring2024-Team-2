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
        username = request.POST.get('username')  # Use .get to avoid KeyError
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required!!!!')
            return render(request, this_page, {'error': 'Username and password are required!'})

        logging.info(f"Logging in as {username}")
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid credentials!!')
            return render(request, this_page, {'error': 'Invalid credentials!'})

        logging.info(f"{user.user_type=}")
        fetch_type = getattr(user, 'user_type', None)
        if fetch_type == user_type:
            login(request, user)
            logging.info(f"Logged in {user=}")
            return render(request, destination)
        else :
            if(fetch_type == 'landlord'):
                messages.error(request, 'Please provide user credentials to login as User !!')
                return render(request, this_page, {'error': 'Invalid user type!'})
            else :
                messages.error(request, 'Please provide landlord credentials to login as Landlord !!')
                return render(request, this_page, {'error': 'Invalid user type!'})
                
    else:
        return render(request, this_page)

def landlord_login(request):
    return login_process(
        request, 
        user_type="landlord", 
        this_page="login/landlord_login.html", 
        destination="landlord_homepage.html"
    )
    
def user_login(request):
    return login_process(
        request, 
        user_type="user", 
        this_page="login/user_login.html", 
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

