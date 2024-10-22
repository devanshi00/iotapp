# mqtt_client.py

import paho.mqtt.client as paho
from paho import mqtt
# import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import asyncio
import json, logging
# from users.models import Sensor,SensorMeasurement
# MQTT connection settings
broker_address = "7957a33dd9d64f539a01cf7ce0d01754.s1.eu.hivemq.cloud"
broker_port = 8883
username = "Dikshant"
password = "Agrawal@098"
client_publish_topic = "HK_Sub1"
client_subscribe_topic = "HK_Pub1"

# Global variable to track message reception
message_received = False
data = ""
channel_layer = get_channel_layer()


# def on_message(client, userdata, msg):
#     global data
#     try:
#         data = json.loads(msg.payload.decode().strip())
#         result = data.get("Result")
#         status = data.get("Status")

#         loop = asyncio.get_event_loop()

#         if result == "Awaiting":
#             loop.run_in_executor(None, async_send_status, status)
        
#         elif result == "Calculated":
#             temperature = data.get("Temperature")
#             loop.run_in_executor(None, async_send_status_and_temperature, status, temperature)

#     except (json.JSONDecodeError, KeyError) as e:
#         print(f"Error decoding message: {e}")

# async def async_send_status(status):
#     await channel_layer.group_send(
#         "temperature_group",
#         {
#             "type": "temperature_message",
#             "message": json.dumps({"Status": status}),
#         }
#     )

# async def async_send_status_and_temperature(status, temperature):
#     await channel_layer.group_send(
#         "temperature_group",
#         {
#             "type": "temperature_message",
#             "message": json.dumps({
#                 "Status": status,
#                 "Temperature": temperature,
#             }),
#         }
#     )

def on_message(client, userdata, msg):
    global data
    # Decode the received message
    try:
        data = json.loads(msg.payload.decode().strip())  # Assuming data is in JSON format
        result = data.get("Result")
        status = data.get("Status")
        
        # If "Result" is "Awaiting", send only the "Status" in JSON format
        if result == "Awaiting":
            async_to_sync(channel_layer.group_send)(
                "temperature_group",
                {
                    "type": "temperature_message",
                    "message": json.dumps({
                        "Status": status
                    })  # JSON formatted message
                }
            )
        
        # If "Result" is "Calculated", send both "Status" and "Temperature" in JSON format
        elif result == "Success":
            temperature = data.get("Temperature")
            async_to_sync(channel_layer.group_send)(
                "temperature_group",
                {
                    "type": "temperature_message",
                    "message": json.dumps({
                        "Status": status,
                        "Temperature": temperature
                    })  # JSON formatted message
                }
            )
                
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error decoding message: {e}")




def setup_mqtt_client():
    """Set up and return the MQTT client."""
    client = paho.Client(client_id="", protocol=paho.MQTTv5)
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(username, password)
    client.connect(broker_address, broker_port, 60)
    
    # Assign the on_message callback
    client.on_message = on_message
    client.loop_start()  # Start the MQTT loop

    return client

# Set up the MQTT client when this module is imported
client = setup_mqtt_client()
client.subscribe(client_subscribe_topic)