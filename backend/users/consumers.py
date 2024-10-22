import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from django.utils import timezone
from decimal import Decimal
from .models import DoctorData, PatientData
# from .serializers import DoctorDataSerializer, PatientDataSerializer
from asgiref.sync import sync_to_async, async_to_sync
from users.mqtt_client import client,client_publish_topic
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.conf import settings

User = get_user_model()
# class MQTTTopicConsumer(AsyncWebsocketConsumer):
#     def __init__(self):
#         super().__init__()
        

#     async def connect(self):
#         # This method is called when the WebSocket connection is opened
#         self.user = None
        
#         # Retrieve JWT token from the headers (optional, you can add authentication here if needed)
#         # token = self.scope['query_string'].decode().split('=')[-1]  # assuming 'token=<JWT>'
#         await self.accept()
        
#         # Send an initial message to confirm the WebSocket connection
#         await self.send(text_data=json.dumps({'status': 'connected'}))

#     async def disconnect(self, close_code):
#         # This method is called when the WebSocket connection is closed
#         pass

#     async def receive(self, text_data):
#         """ Handle messages received via WebSocket for subscribing and publishing topics. """
#         text_data_json = json.loads(text_data)
        
#         # Extract message type, device_id for Subscribe or Publish action
#         message_type = text_data_json.get("message")
        
#         if message_type == "Subscribe":
#             # Set the subscribe topic based on the device_id
#             device_id = text_data_json.get("device_id")
            
#             if not device_id:
#                 await self.send(text_data=json.dumps({"error": "device_id is missing"}))
#                 return
            
#             # Dynamically create and set the MQTT subscribe topic based on the device_id
#             client_subscribe_topic = f"HK_Pub{device_id}"
            
#             # Subscribe to the topic (async call to client.subscribe)
#             client.subscribe(client_subscribe_topic)
            
#             # Send a confirmation back to the frontend
#             await self.send(text_data=json.dumps({
#                 'status': 'Subscribed to topic',
#                 'subscribe_topic': client_subscribe_topic
#             }))

            
#             # Dynamically create and set the MQTT publish topic based on the device_id
#             client_publish_topic = f"HK_Sub{device_id}"
            
#         else:
#             await self.send(text_data=json.dumps({
#                 'error': 'Invalid message type'
#             }))

    

class VitalDataConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
       

    async def connect(self):
        self.user = None

        # Retrieve JWT token from the headers
        token = self.scope['query_string'].decode().split('=')[-1]  # assuming 'token=<JWT>'
        
        # Authenticate the user using JWT
        try:
            validated_token = await self.get_validated_token(token)
            self.user = await self.get_user_from_token(validated_token)

            if self.user.is_authenticated:
                self.role = await self.get_user_role()  # Check for role asynchronously
                await self.accept()
                await self.send(text_data=json.dumps({'status': 'connected', 'user': str(self.user), 'role': self.role}))
                
                # Join the sensor-specific group (room)
                await self.channel_layer.group_add(
                "temperature_group",  # Same group as in the MQTT callback
                 self.channel_name
              )
                # await self.accept()



        except InvalidToken:
            await self.send(text_data=json.dumps({'error': 'Invalid token'}))
            await self.close()

    async def disconnect(self, close_code):
        """ Handle WebSocket disconnection. """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """ Handle messages received via WebSocket. """
        text_data_json = json.loads(text_data)
        
        # Extract message type and device_id (for Subscribe) or topic (for Publish)
        message_type = text_data_json.get("message")
        
        
            
        # Publish the data to the specified topic
        client.publish(client_publish_topic,payload=message_type)
          
        
        if not message_type:
            await self.send(text_data=json.dumps({
                'error': 'Invalid message type'
            }))

        # Optionally, send a confirmation back to the frontend
        




    async def temperature_message(self, event):
        """ Handle messages received in the temperature group. """
        message = event['message']
        
        # Parse the message (assuming JSON format)
        message_data = json.loads(message)
        
        # Check if the message contains both 'Status' and 'Temperature'
        status = message_data.get("Status")
        temperature = message_data.get("Temperature")
        
        if status and temperature:
            # Send only the Status to the frontend
            await self.send(text_data=json.dumps({
                'Status': status
            }))
            
            # Save the temperature to the database based on the user role
            await self.save_temperature_to_db(temperature)

        else:
            # If the message doesn't contain a Temperature, send the entire message to the frontend
            await self.send(text_data=json.dumps(message_data))


    @sync_to_async
    def save_temperature_to_db(self, temperature):
        """ Save or update temperature based on user role (doctor or patient). """
        if self.role == 'doctor':
            # Get the doctor's profile
            doctor_profile = self.user.doctorprofile
            
            # Check if a record exists for this doctor, if so, update it; otherwise, create a new one
            doctor_data, created = DoctorData.objects.get_or_create(
                doctor=doctor_profile,
                defaults={'temperature': Decimal(temperature), 'created_at': timezone.now()}
            )
            if not created:  # If it already existed, update the temperature
                doctor_data.temperature = Decimal(temperature)
                doctor_data.save()

        elif self.role == 'patient':
            # Get the patient's profile
            patient_profile = self.user.patientprofile
            
            # Check if a record exists for this patient, if so, update it; otherwise, create a new one
            patient_data, created = PatientData.objects.get_or_create(
                patient=patient_profile,
                defaults={'temperature': Decimal(temperature), 'created_at': timezone.now()}
            )
            if not created:  # If it already existed, update the temperature
                patient_data.temperature = Decimal(temperature)
                patient_data.save()

    @sync_to_async
    def get_validated_token(self, token):
        """ Validate the JWT token. """
        return UntypedToken(token)

    @sync_to_async
    def get_user_from_token(self, validated_token):
        """ Retrieve the user based on the validated JWT token. """
        return User.objects.get(id=validated_token['user_id'])

    @sync_to_async
    def get_user_role(self):
        """ Get the role of the user (doctor or patient). """
        if hasattr(self.user, 'doctorprofile'):
            return "doctor"
        elif hasattr(self.user, 'patientprofile'):
            return "patient"
        return "unknown"
