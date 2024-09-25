# #views.py
# from django.contrib.auth import authenticate, login
# from rest_framework import generics, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from .models import CustomUser, PatientProfile
# from .serializers import RegisterSerializer, LoginSerializer, PatientProfileSerializer
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.views import APIView

# class RegisterView(generics.CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = RegisterSerializer
#     permission_classes = [AllowAny]

# class LoginView(generics.GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request, *args, **kwargs):
#         username = request.data.get("username")
#         password = request.data.get("password")
#         user = authenticate(username=username, password=password)
#         refresh = RefreshToken.for_user(user)
#         if user:
#             serializer = RegisterSerializer(user)
#             return Response(
#                 {"user": serializer.data, "token":{"access":str(refresh.access_token),"refresh":str(refresh)}},
#                 status=status.HTTP_200_OK,
#             )
#         return Response(
#             {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
#         )

# from rest_framework.response import Response
# from rest_framework import status

# class PatientProfileView(APIView):
#     serializer_class = PatientProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user  # Get the authenticated user from the request

#         try:
#             # Try to find a patient profile for the user
#             patient = PatientProfile.objects.get(user=user)
#             serializer = self.serializer_class(patient)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except PatientProfile.DoesNotExist:
#             # If the patient doesn't exist, create a new one
#             patient = PatientProfile.objects.create(user=user)
#             patient.save()  # Save the new patient record
#             serializer = self.serializer_class(patient)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def post(self, request):
#         # Handle POST request to update the patient profile data
#         user = request.user
#         try:
#             # Try to find the patient profile for the user
#             patient = PatientProfile.objects.get(user=user)
#         except PatientProfile.DoesNotExist:
#             return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = self.serializer_class(patient, data=request.data, partial=True)  # partial=True allows partial updates
#         if serializer.is_valid():
#             serializer.save()  # Save the updated patient data
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request):
#         # Handle PUT request to update the patient profile
#         user = request.user
#         try:
#             # Try to find the patient profile for the user
#             patient = PatientProfile.objects.get(user=user)
#         except PatientProfile.DoesNotExist:
#             return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = self.serializer_class(patient, data=request.data)  # Update with complete data
#         if serializer.is_valid():
#             serializer.save()  # Save the updated patient data
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py
from django.contrib.auth import authenticate, login
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, PatientProfile
from .serializers import RegisterSerializer, LoginSerializer, PatientProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
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


class PatientProfileView(APIView):
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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