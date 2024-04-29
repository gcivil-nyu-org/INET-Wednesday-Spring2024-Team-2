from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Rental_Listings


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        "username",
        "email",
        "full_name",
        "user_type",
        "is_staff",
        "is_active",
        "s3_doclink",
        "verified",
    ]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("full_name", "email", "user_type")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Status", {"fields": ("verified",)}),
    )


class RentalListingsAdmin(admin.ModelAdmin):
    list_display = (
        "address",
        "price",
        "Landlord_id",
        "neighborhood",
        "rooms",
        "unit_type",
        "beds",
        "baths",
        "sq_ft",
        "zipcode",
        "borough",
        "Submitted_date",
        "Availability_Date",
    )
    # list_filter = ('city', 'zipcode', 'borough')
    # search_fields = ('address', 'city', 'zipcode')
    fieldsets = (
        (None, {"fields": ("address", "price")}),
        ("Details", {"fields": ("rooms", "beds", "baths", "sq_ft", "unit_type")}),
        ("Availability", {"fields": ("Submitted_date", "Availability_Date")}),
        ("Location", {"fields": ("zipcode", "borough", "neighborhood")}),
    )


# Register both admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Rental_Listings, RentalListingsAdmin)
