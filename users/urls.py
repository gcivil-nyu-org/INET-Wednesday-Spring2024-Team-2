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
    path("post_new_listings/", views.add_rental_listing, name="post_new_listings"),
    path("listings/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path(
        "listings/landlord/<int:listing_id>/",
        views.landlord_listing_detail,
        name="landlord_listing_detail",
    ),
    path("toggle_favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.favorites_page, name="favorites_page"),
    path("map/", views.map_view, name="rental_listings_map"),
    path("user/account/", views.profile_view_edit, name="profile_view_edit"),
    path(
        "landlord/account/",
        views.landlord_profile_update,
        name="landlord_profile_update",
    ),
    path(
        "listing/<int:listing_id>/edit/",
        views.edit_rental_listing,
        name="edit_rental_listing",
    ),
    path(
        "listing/<int:listing_id>/delete/",
        views.delete_rental_listing,
        name="delete_rental_listing",
    ),
]
