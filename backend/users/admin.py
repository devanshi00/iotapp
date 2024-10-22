# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, PatientProfile, DoctorProfile,PatientData,DoctorData


class UserAdmin(BaseUserAdmin):
    # This class customizes the way CustomUser is displayed and managed in the Django admin.
    # It inherits from UserAdmin provided by Django, but additional customizations are made.
    model = CustomUser
    list_display = ("username", "email", "role", "unique_id", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "role", "unique_id")

    fieldsets = (
        (None, {"fields": ("username", "password", "unique_id")}),
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
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )
    search_fields = ("username", "email", "unique_id")  # Allow searching by unique_id
    ordering = ("username",)


# Register CustomUser and PatientProfile in the admin site
admin.site.register(CustomUser, UserAdmin)
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(PatientData)
admin.site.register(DoctorData)
