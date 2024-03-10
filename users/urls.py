from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
    path("login/password_reset/", 
        auth_views.PasswordResetView.as_view(template_name="login/password_reset_form.html"),
        name="password_reset_form"),
    path("login/password_reset/done/", 
        auth_views.PasswordResetDoneView.as_view(template_name="login/password_reset_done.html"), 
        name="password_reset_done"),
    path("login/reset/<uidb64>/<token>/", 
        auth_views.PasswordResetConfirmView.as_view(template_name="login/password_reset_confirm.html"),
        name="password_reset_confirm"),
    
]
