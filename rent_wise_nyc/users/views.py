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

def landlord_login(request):
    logging.info("hello here at login page")
    if request.method == 'POST':
        logging.info("if request")
        username = request.POST['username']
        password = request.POST['password']
        logging.info(f"logging in as {username}")
        user = authenticate(username=username, password=password)
        logging.info(f"{user=}")
        if user is not None:
            login(request, user)
            return render(request,"landlords.html")
        else:
            # Return an error message or render the login page again
            messages.error(request,'Invalid credentials!!')
            logging.info("invalid credentials")
            return render(request, 'registration/login.html', {'error': 'Invalid credentials!!'})
    else:
        return render(request,"registration/login.html")

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

