from django.urls import path
from .consumers import VitalDataConsumer
# from .consumers import MQTTTopicConsumer

websocket_urlpatterns = [
    path('ws/vitals/', VitalDataConsumer.as_asgi()),
    # path('ws/mqtt/', MQTTTopicConsumer.as_asgi()),
]