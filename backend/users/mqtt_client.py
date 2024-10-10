import asyncio
import socket
import uuid
import paho.mqtt.client as mqtt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# MQTT connection settings
broker_address = "7957a33dd9d64f539a01cf7ce0d01754.s1.eu.hivemq.cloud"
broker_port = 8883
username = "Dikshant"
password = "Agrawal@098"
client_publish_topic = "HK_Sub1"
client_subscribe_topic = "HK_Pub1"

# Generating a unique client ID
client_id = 'Dikshant-client/' + str(uuid.uuid4())
print("Using client_id: " + client_id)


class AsyncioHelper:
    def __init__(self, loop, client):
        self.loop = loop
        self.client = client
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):
        print("Socket opened")

        def cb():
            print("Socket is readable, calling loop_read")
            client.loop_read()

        self.loop.add_reader(sock, cb)
        self.misc = self.loop.create_task(self.misc_loop())

    def on_socket_close(self, client, userdata, sock):
        print("Socket closed")
        self.loop.remove_reader(sock)
        self.misc.cancel()

    def on_socket_register_write(self, client, userdata, sock):
        print("Watching socket for writability.")

        def cb():
            print("Socket is writable, calling loop_write")
            client.loop_write()

        self.loop.add_writer(sock, cb)

    def on_socket_unregister_write(self, client, userdata, sock):
        print("Stop watching socket for writability.")
        self.loop.remove_writer(sock)

    async def misc_loop(self):
        print("misc_loop started")
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
        print("misc_loop finished")


class AsyncMqttExample:
    def __init__(self, loop):
        self.loop = loop
        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set(username, password)  # Set username and password for MQTT connection
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        print(f"Connected with reason code: {reason_code}")
        print("Subscribing to topic: " + client_subscribe_topic)
        client.subscribe(client_subscribe_topic)

    def on_message(self, client, userdata, msg):
        print("Received message: {}".format(msg.payload.decode()))
        # Send the message back to the WebSocket via Django Channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "vitals_group",  # The WebSocket group
            {
                "type": "vitals_message",
                "message": msg.payload.decode(),
            }
        )

    def on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        print(f"Disconnected with reason code: {reason_code}")

    async def start(self):
        aioh = AsyncioHelper(self.loop, self.client)

        # Connect to the broker
        self.client.connect(broker_address, broker_port, 60)
        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

        # Keep the client running to receive messages
        while True:
            await asyncio.sleep(60)

    async def publish_message(self, message):
        if self.client.is_connected():
            print(f"Publishing message to topic {client_publish_topic}: {message}")
            self.client.publish(client_publish_topic, message)
        else:
            print("Client is not connected, unable to publish.")


# The function to be used in the ASGI app
async def mqtt_startup():
    """Run the MQTT client asynchronously during ASGI startup."""
    loop = asyncio.get_event_loop()
    mqtt_client = AsyncMqttExample(loop)
    await mqtt_client.start()


# Helper function to publish message on demand
async def publish_temperature():
    """Publish a temperature message when requested by WebSocket."""
    loop = asyncio.get_event_loop()
    mqtt_client = AsyncMqttExample(loop)
    await mqtt_client.publish_message("Temperature")
