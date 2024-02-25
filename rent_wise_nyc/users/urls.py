from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("logout", views.logout_view),
    path('registration/login/', views.landlord_login, name='login'),
    path('landlord/', views.landlord_home, name='landlord'),
    path('users/', views.user_home, name='user'),
]