# views.py
from django.contrib.auth import authenticate, login
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, PatientProfile, DoctorProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
  
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import CustomUser

from django.http import JsonResponse
from django.core.files.storage import default_storage
import paho.mqtt.client as paho
from paho import mqtt
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from datetime import datetime
import json
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
import json
from decimal import Decimal
from datetime import datetime
from .models import CustomUser, PatientProfile, DoctorProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PatientProfileSerializer,
    DoctorProfileSerializer,
   
)
# from users.mqtt_client import client,message_received,data

# # Accessing the global variable from manage.py
# from manage import data, message_received


class RegisterView(generics.CreateAPIView):
    # HTTP Method: POST request
    queryset = CustomUser.objects.all()  # retrieves all customuser objects
    serializer_class = (
        RegisterSerializer  # Handles user registration using the RegisterSerializer
    )
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer  # Authenticates users using the LoginSerializer

    def post(
        self, request, *args, **kwargs
    ):  # POST request to log in the user by passing username and password
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        # After authentication, it generates JWT tokens (access and refresh) using rest_framework_simplejwt.tokens.RefreshToken.
        refresh = RefreshToken.for_user(user)
        if user:
            serializer = RegisterSerializer(user)
            return Response(
                {
                    "user": serializer.data,
                    "token": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )


from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage


class PatientProfileView(APIView):  # inherits from APIView
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the authenticated user from the request

        try:
            # Try to find a patient profile for the user
            patient = PatientProfile.objects.get(user=user)
            serializer = self.serializer_class(patient)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except PatientProfile.DoesNotExist:
            # If the patient doesn't exist, create a new one
            patient = PatientProfile.objects.create(user=user)
            patient.save()  # Save the new patient record
            serializer = self.serializer_class(patient)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )  # Returns serialized profile data in JSON

    def post(self, request):
        # Handle POST request to update the patient profile data
        user = request.user
        try:
            # Try to find the patient profile for the user
            patient = PatientProfile.objects.get(user=user)
        except PatientProfile.DoesNotExist:
            return Response(
                {"error": "Patient profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(
            patient, data=request.data, partial=True
        )  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()  # Save the updated patient data
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Handle PUT request to update the patient profile
        user = request.user
        try:
            # Try to find the patient profile for the user
            patient = PatientProfile.objects.get(user=user)
        except PatientProfile.DoesNotExist:
            return Response(
                {"error": "Patient profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Check if the profile picture is being updated
        if "profile_picture" in request.data and patient.profile_picture:
            # Delete the old profile picture
            default_storage.delete(patient.profile_picture.name)  # Remove the old file

        serializer = self.serializer_class(
            patient, data=request.data
        )  # Update with complete data
        if serializer.is_valid():
            serializer.save()  # Save the updated patient data
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for handling doctor profile data
class DoctorProfileView(APIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the authenticated user from the request

        try:
            # Try to find a doctor profile for the user
            doctor = DoctorProfile.objects.get(user=user)
            serializer = self.serializer_class(doctor)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except DoctorProfile.DoesNotExist:
            # If the doctor doesn't exist, create a new one
            doctor = DoctorProfile.objects.create(user=user)
            doctor.save()  # Save the new doctor record
            serializer = self.serializer_class(doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request):
        # Handle POST request to update the doctor profile data
        user = request.user
        try:
            # Try to find the doctor profile for the user
            doctor = DoctorProfile.objects.get(user=user)
        except DoctorProfile.DoesNotExist:
            return Response(
                {"error": "Doctor profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(
            doctor, data=request.data, partial=True
        )  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()  # Save the updated doctor data
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Handle PUT request to update the doctor profile
        user = request.user
        try:
            # Try to find the doctor profile for the user
            doctor = DoctorProfile.objects.get(user=user)
        except DoctorProfile.DoesNotExist:
            return Response(
                {"error": "Doctor profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the profile picture is being updated
        if "profile_picture" in request.data and doctor.profile_picture:
            # Delete the old profile picture
            default_storage.delete(doctor.profile_picture.name)  # Remove the old file

        serializer = self.serializer_class(
            doctor, data=request.data
        )  # Update with complete data
        if serializer.is_valid():
            serializer.save()  # Save the updated doctor data
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientProfileListView(APIView):
    # API view to retrieve all patient profiles.
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET requests to return all patient profiles.
        """
        profiles = PatientProfile.objects.all()  # Query to get all patient profiles
        serializer = PatientProfileSerializer(
            profiles, many=True
        )  # Serialize the profiles
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )  # Return the response

# views.py

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import PatientProfile, DoctorProfile, PatientData, DoctorData
# from .serializers import PatientDataSerializer, DoctorDataSerializer
# from decimal import Decimal
# from datetime import datetime
# import json
# from users.mqtt_client import client, message_received, client_publish_topic  # Correct import

# client_publish_base_topic = "HK_Sub"
# client_subscribe_base_topic = "HK_Pub"

# # def on_message(client, userdata, msg):
# #     # print("Received message: ", msg.payload.decode().strip())
# #     global message_received , data
# #     message_received = True
# #     data = msg.payload.decode().strip()
# #     return data

# # class DeviceIdView(APIView):
#     permission_classes = [IsAuthenticated]

    # def post(self, request):
    #     global client_publish_topic, client_subscribe_topic

    #     # Extract device_id from request data
    #     device_id = request.data.get("device_id")
    #     if not device_id:
    #         return Response({"error": "Device ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    #     # Set MQTT topics based on device ID
    #     client_publish_topic = f"HK_Sub{device_id}"
    #     client_subscribe_topic = f"HK_Pub{device_id}"

    #     # Subscribe to the new topic
    #     client.subscribe(client_subscribe_topic)

    #     return Response({
    #         "message": f"Topics set for device ID {device_id}",
    #         "subscribe_topic": client_subscribe_topic,
    #         "publish_topic": client_publish_topic
    #     }, status=status.HTTP_200_OK)
    
# class VitalsDataView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """
#         Handle POST request to publish a message and wait for the response from the MQTT server.
#         """
#         user = request.user  # This is the CustomUser instance
#         role = user.role  # This fetches the user's role (doctor, patient, or admin)

#         print(f"User Role: {role}")  # For debugging

#         # Ensure the user is authenticated
#         if not user.is_authenticated:
#             return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

#         # Get the message type and device ID from the POST request
#         message_type = request.data.get("message", None)
       
#         client.publish(client_publish_topic, payload=message_type, qos=2)

#         global message_received,data
#         message_received = False
#         while not message_received:
#             client.on_message = on_message
#             pass

#         temperature_data = data  # The response data

#         # Debugging output
#         print("Raw Temperature Data:", temperature_data)

#         try:
#             # Check if temperature_data is a stringified JSON
#             temperature_json = json.loads(temperature_data)
#             temperature_value = temperature_json.get("Temperature")

#             # Ensure temperature value is present
#             if temperature_value is not None:
#                 if role == "doctor":
#                     profile = DoctorProfile.objects.get(user=user)

#                     # Create and store the DoctorData instance associated with the profile
#                     doctor_data = DoctorData(
#                         doctor=profile, temperature=Decimal(temperature_value),
#                         created_at=datetime.now()
#                     )
#                     doctor_data.save()

#                     # Serialize the doctor data
#                     serializer = DoctorDataSerializer(doctor_data)
#                     return Response(serializer.data, status=status.HTTP_200_OK)

#                 elif role == "patient":
#                     profile = PatientProfile.objects.get(user=user)

#                     # Create and store the PatientData instance associated with the profile
#                     patient_data = PatientData(
#                         patient=profile, temperature=Decimal(temperature_value),
#                         created_at=datetime.now()
#                     )
#                     patient_data.save()

#                     # Serialize the patient data
#                     serializer = PatientDataSerializer(patient_data)
#                     return Response(serializer.data, status=status.HTTP_200_OK)

#                 else:
#                     return Response({"error": "User role not recognized"}, status=status.HTTP_403_FORBIDDEN)

#             else:
#                 return Response({"error": "Temperature value not found"}, status=status.HTTP_400_BAD_REQUEST)

#         except json.JSONDecodeError:
#             return Response({"error": "Invalid temperature data format"}, status=status.HTTP_400_BAD_REQUEST)
