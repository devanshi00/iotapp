# serializers.py
# for handling data transformation between Django models and JSON representations
# serializers are used by Django REST Framework (DRF) to handle API requests and responses
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser,PatientProfile,DoctorProfile
# from .models import PatientData,DoctorData

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

# class PatientDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PatientData
#         fields = ['patient', 'temperature','created_at']  

# class DoctorDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DoctorData
#         fields = ['doctor', 'temperature','created_at']