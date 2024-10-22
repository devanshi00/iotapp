import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from django.utils import timezone
from decimal import Decimal
# from .models import DoctorData, PatientData, PatientProfile, DoctorProfile
# from .serializers import DoctorDataSerializer, PatientDataSerializer
from asgiref.sync import sync_to_async
from users.mqtt_client import client, message_received, data, client_publish_topic, on_message
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.conf import settings

User = get_user_model()

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
                self.room_group_name = f"TEMP-001"
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

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
        message_type = text_data_json.get("message")
        await self.send(text_data=json.dumps({"message": message_type}))

    async def sensor_created(self, event):
        """ Handle sensor.created messages sent from the signal. """
        sensor_id = event['sensor_id']
        name = event['name']

        # Send the sensor created message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'sensor.created',
            'sensor_id': sensor_id,
            'name': name,
        }))

    async def measurement_created(self, event):
        """ Handle measurement.created messages sent from the signal. """
        sensor_id = event['sensor_id']
        value = event['value']
        timestamp = event['timestamp']

        # Send the sensor measurement message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'measurement.created',
            'sensor_id': sensor_id,
            'value': value,
            'timestamp': timestamp,
        }))

    async def sensor_deleted(self, event):
        """ Handle sensor.deleted messages sent from the signal. """
        sensor_id = event['sensor_id']

        # Send the sensor deleted message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'sensor.deleted',
            'sensor_id': sensor_id,
        }))

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
