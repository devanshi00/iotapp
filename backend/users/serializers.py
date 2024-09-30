# serializers.py
# for handling data transformation between Django models and JSON representations
# serializers are used by Django REST Framework (DRF) to handle API requests and responses
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser, PatientProfile, DoctorProfile
from .models import PatientData

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "unique_id"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        # Takes username, email, password, confirm_password, and role as input.
        model = CustomUser
        fields = ["username", "email", "password", "confirm_password", "role"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        return data

    def create(self, validated_data):
        # In the create method, it saves the user to the database, hashing the password using set_password to securely store it.
        user = CustomUser(
            username=validated_data["username"],
            email=validated_data["email"],
            role=validated_data["role"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    # Takes username and password as input
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError(
                "Both username and password are required."
            )

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        return data


class PatientProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    unique_id = serializers.CharField(source="user.unique_id", read_only=True)
    # Includes the CustomUserSerializer for the user field, meaning that related user data is displayed in a nested format.
    # Exposes unique_id from the related CustomUser model using source="user.unique_id

    class Meta:
        model = PatientProfile
        fields = [
            "user",
            "unique_id",
            "name",
            "dob",
            "blood_group",
            "height",
            "weight",
            "profile_picture",
        ]


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = "__all__"

class PatientDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientData
        fields = ['user', 'temperature']  # Only include user and temperature fields
        read_only_fields = ['user']  # Making the user field read-only, as it's derived from the request

    def update(self, instance, validated_data):
        """Update the instance's temperature field based on validated data."""
        instance.temperature = validated_data.get('temperature', instance.temperature)
        instance.save()
        return instance

    def validate_temperature(self, value):
        """Custom validation for temperature."""
        if value < -100 or value > 100:  # Example boundary values
            raise serializers.ValidationError("Temperature must be between -100 and 100 degrees.")
        return value