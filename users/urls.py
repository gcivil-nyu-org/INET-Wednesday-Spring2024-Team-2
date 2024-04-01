from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import placeholder_view

urlpatterns = [
    path("", views.home, name="index"),
    path("logout", views.logout_view),
    path("signup/user_up", views.user_signup, name="user_signup"),
    path("login/landlord_login", views.landlord_login, name="landlord_login"),
    path("login/user_login", views.user_login, name="user_login"),
    path("landlord/", views.landlord_home, name="landlord"),
    path("users/", views.user_home, name="user"),
    path("landlord/home/", views.landlord_home, name="landlord_homepage"),
    path("user/home/", views.user_home, name="user_homepage"),
    path("signup/landlord_signup/", views.landlord_signup, name="landlord_signup"),
    path(
        "login/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="login/password_reset_form.html",
            email_template_name="login/password_reset_email.html",
            subject_template_name="login/password_reset_subject.txt",
        ),
        name="password_reset_form",
    ),
    path(
        "login/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="login/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "login/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="login/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "login/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="login/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("rentalspage/", views.rentals_page, name="rentalspage"),
    path("placeholder/", placeholder_view, name="placeholder"),
    path("toggle_favorite/", views.toggle_favorite, name="toggle_favorite"),
]
