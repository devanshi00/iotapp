import os
import asyncio
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import users.routing
from users.mqtt_client import mqtt_startup

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

# Start the MQTT client using the event loop
async def main():
    await mqtt_startup()

# Run the event loop in the main thread
if __name__ == "__main__":
    asyncio.run(main())
