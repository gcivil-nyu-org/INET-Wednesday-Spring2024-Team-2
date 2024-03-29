"""
Django settings for rent_wise_nyc project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.environ.get("PROD_SECRET_KEY") #TODO
SECRET_KEY = "django-insecure-0!koe(9n(u$8x3g24sctwu^&=&pv%+m70xa3+gqw7uv32h3ej_"


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "rent-wise-prod.eba-3qbiyspq.us-east-1.elasticbeanstalk.com",
]

# Application definition
SITE_ID = 5

DEFAULT_FROM_EMAIL = "rentwisenyc@gmail.com"
EMAIL_BACKEND = "django_ses.SESBackend"
