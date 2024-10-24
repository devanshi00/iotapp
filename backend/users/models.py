# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
import random
import string
from datetime import datetime
# Function to generate unique ID
def generate_unique_id(prefix):
    """Generate a unique ID in the format: prefix + 5 random digits."""
    return f"{prefix}{''.join(random.choices(string.digits, k=5))}"


class CustomUser(AbstractUser):
    # Django AbstractUser already provides id(autofield,If no other primary key is defined, Django automatically adds an id field as primary key.),username,first_name,last_name,email,password fields
    # we have added role,unique_id
    ROLE_CHOICES = [
        ("doctor", "Doctor"),
        ("patient", "Patient"),
        ("admin", "Admin"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="patient")
    email = models.EmailField(unique=True)
    unique_id = models.CharField(
        max_length=10, blank=True, unique=True
    )  # New field for unique ID

    # Overrides the save method to ensure the unique_id is set when a new user is created.
    # The unique_id is crucial to link with either the PatientProfile or DoctorProfile.

    def save(self, *args, **kwargs):
        # Check if user doesn't have an ID yet, then generate one based on the role
        if not self.unique_id:
            if self.role == "patient":
                self.unique_id = generate_unique_id("ABU")
            elif self.role == "doctor":
                self.unique_id = generate_unique_id("ABD")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class PatientProfile(models.Model):
    # Has a one-to-one relationship with the CustomUser model via the unique_id.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="unique_id"
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )

    def __str__(self):
        return self.user.username


# Signal to delete profile picture when a PatientProfile is deleted
@receiver(pre_delete, sender=PatientProfile)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    if instance.profile_picture:
        # Remove the profile picture from the file system
        if default_storage.exists(instance.profile_picture.name):
            default_storage.delete(instance.profile_picture.name)


# If you want to ensure that the profile is deleted when the CustomUser is deleted:
@receiver(pre_delete, sender=CustomUser)
def delete_user_profile(sender, instance, **kwargs):
    if instance.role == "patient":
        try:
            instance.patientprofile.delete()
        except PatientProfile.DoesNotExist:
            pass  # If profile doesn't exist, no action needed


class DoctorProfile(models.Model):
    # has a one-to-one relationship with the CustomUser model via the unique_id.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="unique_id"
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)
    experience = models.PositiveIntegerField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )

    def __str__(self):
        return self.user.username


# Signal to delete profile picture when a PatientProfile is deleted
@receiver(pre_delete, sender=DoctorProfile)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    if instance.profile_picture:
        # Remove the profile picture from the file system
        if default_storage.exists(instance.profile_picture.name):
            default_storage.delete(instance.profile_picture.name)


# If you want to ensure that the profile is deleted when the CustomUser is deleted:
@receiver(pre_delete, sender=CustomUser)
def delete_user_profile(sender, instance, **kwargs):
    if instance.role == "doctor":
        try:
            instance.doctorprofile.delete()
        except DoctorProfile.DoesNotExist:
            pass  # If profile doesn't exist, no action needed


class DoctorData(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="vitals")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose_samples = models.JSONField(null=True, blank=True)  # Store samples as JSON
    oxygen_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heart_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    spo2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PatientData(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="vitals")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose_samples = models.JSONField(null=True, blank=True)  # Store samples as JSON
    oxygen_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heart_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    spo2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class VitalHistoryPatient(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="vital_history")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose_samples = models.JSONField(null=True, blank=True)
    oxygen_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heart_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    spo2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

class VitalHistoryDoctor(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="vital_history")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glucose_samples = models.JSONField(null=True, blank=True)
    oxygen_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heart_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    spo2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

