# mqtt_client.py
import random
import paho.mqtt.client as paho
from paho import mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import asyncio
import json, logging

# MQTT connection settings
broker_address = "7957a33dd9d64f539a01cf7ce0d01754.s1.eu.hivemq.cloud"
broker_port = 8883
username = "Dikshant"
password = "Agrawal@098"

channel_layer = get_channel_layer()

# Mapping subjects to their respective WebSocket group types
subject_group_mapping = {
    "Hardware Configuration": "hardware_group_",
    "Glucose": "glucose_group_",
    "Temperature": "temperature_group_",
    "Oximeter": "oximeter_group_"
}

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages and forward them to the appropriate WebSocket group based on the subject."""
    try:
        if msg.retain == 1:
            print("This is a retained message", msg.payload)
        else:
            data = json.loads(msg.payload.decode().strip())
            device_id = data.get("DeviceID")
            subject = data.get("Subject")

            # Determine the WebSocket group based on the subject
            group_prefix = subject_group_mapping.get(subject)
            if group_prefix:
                group_name = f"{group_prefix}{device_id}"
            else:
                print(f"Unrecognized subject: {subject}")
                return
            
            if subject == "Hardware Configuration":
                status = data.get("Status")
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "hardware_message",
                        "message": json.dumps({
                            "Status": status
                        })
                    }
                )

            elif subject == "Glucose":
                glucose_level = data.get("Glucose")
                samples = data.get("Samples")
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "glucose_message",
                        "message": json.dumps({
                            
                            "Glucose": glucose_level,
                            "Samples": samples
                        })
                    }
                )

            elif subject == "Temperature":
                result = data.get("Result")
                status = data.get("Status")
            # If "Result" is "Awaiting", send only the "Status" in JSON format
                if result == "Awaiting":
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "temperature_message",
                            "message": json.dumps({
                                "Status": status
                            })
                        }
                    )
                
                # If "Result" is "Success", send both "Status" and "Temperature" (or relevant fields for other subjects)
                elif result == "Success":
                    temperature = data.get("Temperature")
                    # Check if temperature exists for subjects like Temperature, otherwise send Status only
                   
                    async_to_sync(channel_layer.group_send)(
                            group_name,
                            {
                                "type": "temperature_message",
                                "message": json.dumps({
                                    "Status": status,
                                    "Temperature": temperature
                                })
                            }
                        )
                elif result == "Retry":
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "temperature_message",
                            "message": json.dumps({
                                "Status": status
                            })
                        }
                    )
            elif subject == "Oximeter":
                result = data.get("Result")
                status = data.get("Status") 
                # If "Result" is "Awaiting", send only the "Status" in JSON format
                if result == "Awaiting":
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "oximeter_message",
                            "message": json.dumps({
                                "Status": status
                            })
                        }
                    )
                
                # If "Result" is "Success", send both "Status" and "Temperature" (or relevant fields for other subjects)
                elif result == "Success":
                    spo2 = data.get("SPO2")
                    heartrate = data.get("Heart_Rate")
                    # Check if temperature exists for subjects like Temperature, otherwise send Status only
                   
                    async_to_sync(channel_layer.group_send)(
                            group_name,
                            {
                                "type": "oximeter_message",
                                "message": json.dumps({
                                    "Status": status,
                                    "SPO2": spo2,
                                    "Heart_Rate": heartrate
                                })
                            }
                        )
                elif result == "Retry":
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "oximeter_message",
                            "message": json.dumps({
                                "Status": status
                            })
                        }
                    )
                   
                    
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error decoding message: {e}")

def setup_mqtt_client(device_id):
    """Set up and return the MQTT client with dynamic topics."""
    client_id = str(random.randint(1, 50000))
    client = paho.Client(client_id=client_id, protocol=paho.MQTTv5)
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(username, password)
    client.connect(broker_address, broker_port, 60)
    
    # Assign the on_message callback
    client.on_message = on_message
    client.loop_start()
    
    # Subscribe to the dynamic topic based on device_id
    client.subscribe(f"HK_Pub{device_id}")
    return client
