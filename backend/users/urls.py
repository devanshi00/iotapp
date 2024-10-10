# urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    PatientProfileView,
    DoctorProfileView,
    PatientProfileListView,
    # VitalsDataView,
    # DeviceIdView

)


urlpatterns = [
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("patientprofile/", PatientProfileView.as_view(), name="patientprofile"),
    path("doctorprofile/", DoctorProfileView.as_view(), name="doctorprofile"),
    path(
        "patient-profiles/",
        PatientProfileListView.as_view(),
        name="patient-profiles-list",
    ),
    # path('device-id/', DeviceIdView.as_view(), name='vitals_data'),
    # path('vitals/', VitalsDataView.as_view(), name='vitals_data'),
]
