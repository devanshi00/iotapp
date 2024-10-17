# mqtt_client.py

import paho.mqtt.client as paho
from paho import mqtt

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

def on_message(client, userdata, msg):
    global  data
    # message_received = True
    data = msg.payload.decode().strip()
    print(f"Received message: {data}")
    return data
    # print(f"Received message: {data}")

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