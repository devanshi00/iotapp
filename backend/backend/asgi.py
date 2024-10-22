import os
import threading
import asyncio

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import users.routing

# # Import the MQTT client setup function
# from users.mqtt_client import setup_mqtt_client, client_subscribe_topic

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Set up the ASGI application
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            users.routing.websocket_urlpatterns
        )
    ),
})