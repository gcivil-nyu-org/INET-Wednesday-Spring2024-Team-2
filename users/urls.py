from django.urls import path
from . import views
from .views import user_signup

urlpatterns = [
    path("", views.home, name="index"),
    path("logout", views.logout_view),
    path("signup/user_up", user_signup, name="user_signup"),
    path("login/landlord_login", views.landlord_login, name="landlord_login"),
    path("login/user_login", views.user_login, name="user_login"),
    path("landlord/", views.landlord_home, name="landlord"),
    path("users/", views.user_home, name="user"),
    path("landlord/home/", views.landlord_home, name="landlord_homepage"),
    path("user/home/", views.user_home, name="user_homepage"),
    path("password_reset", views.password_reset, name="password_reset"),
]
