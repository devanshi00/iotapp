from django.urls import path
from .consumers import VitalDataConsumer

websocket_urlpatterns = [
    path('ws/vitals/', VitalDataConsumer.as_asgi()),
]