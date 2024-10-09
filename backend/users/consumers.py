import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from django.utils import timezone
from decimal import Decimal
from .models import DoctorData, PatientData, PatientProfile, DoctorProfile
from .serializers import DoctorDataSerializer, PatientDataSerializer
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
        self.data_queue = asyncio.Queue()

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
            else:
                await self.close()

        except InvalidToken:
            await self.send(text_data=json.dumps({'error': 'Invalid token'}))
            await self.close()

    async def disconnect(self, close_code):
        """ Handle WebSocket disconnection. """
        pass  # No special action needed on disconnect

    async def receive(self, text_data):
        """ Handle messages received via WebSocket. """
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("message")

        # Start polling the hardware every 2 seconds
        await self.poll_hardware_for_vital(message_type)

    async def poll_hardware_for_vital(self, message_type):
        """Poll the hardware for vital data (temperature) and send status updates every 2 seconds."""
        result_received = False
        max_time = 90  # 90 seconds timeout after hardware is connected
        start_time = time.time()

        # Publish the message to the hardware once
        await self.send_status("Preparing to publish message...")
        client.publish(client_publish_topic, payload=message_type, qos=2)
        await self.send_status("Message published, waiting for hardware response...")

        # client.publish(client_publish_topic, payload=message_type, qos=2)
        # await self.send_status("Message published, waiting for hardware response...")
        
        # Poll for 90 seconds, sending status updates every 2 seconds
        while not result_received and (time.time() - start_time) < max_time:
            # Wait for hardware response or for 2 seconds
            data=""
            self.wait_for_response()

            # Send status update every 2 seconds while waiting for response
            await self.send_status("Polling hardware...")

            # Check if a response has been received
            hardware_response = data  # `data` should be updated from some external event or callback
            if hardware_response:  # If response is not None, process it
                try:
                    response_json = json.loads(hardware_response)
                    status = response_json.get("Status")
                    temperature = response_json.get("Temperature")
                    result = response_json.get("Result")

                    if result == "retry":
                        await self.send_status("Place your Finger Properly")
                    elif status == "Reading Complete":
                        await self.send_status(f"{temperature} °C, {status}")
                        await self.save_vital_data(temperature)
                        result_received = True
                    else:
                        await self.send_status(f"{status}")

                except json.JSONDecodeError:
                    await self.send_status("Invalid response from hardware")
                break  # Exit the while-loop since a response has been received

        if not result_received:
            await self.send_status("Request timeout. Failed to retrieve vital data.")

    async def wait_for_response(self):
        """Wait for the MQTT response to come in from the hardware."""
        global data
        client.on_message = on_message

        # Wait until data is populated
        while data is None:
            await asyncio.sleep(1)  # Sleep for 1 second
        
        # Data is received, now you can process it or return
        return data  # Optionally return data if needed


    async def send_status(self, message):
        """ Send the status message back to the frontend. """
        await self.send(text_data=json.dumps({
            "status": message
        }))

    @sync_to_async
    def save_vital_data(self, temperature):
        """ Save the temperature data to the database. """
        user = self.user
        role = self.role

        if role == "doctor":
            profile = DoctorProfile.objects.get(user=user)

            # Create and store the DoctorData instance associated with the profile
            doctor_data = DoctorData(
                doctor=profile, temperature=Decimal(temperature),
                created_at=timezone.now()
            )
            doctor_data.save()

        elif role == "patient":
            profile = PatientProfile.objects.get(user=user)

            # Create and store the PatientData instance associated with the profile
            patient_data = PatientData(
                patient=profile, temperature=Decimal(temperature),
                created_at=timezone.now()
            )
            patient_data.save()

        else:
            raise ValueError("Unknown user role")

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
        """ 
        Get the role of the user (doctor or patient) based on the profile associated with the user.
        """
        if hasattr(self.user, 'doctorprofile'):
            return "doctor"
        elif hasattr(self.user, 'patientprofile'):
            return "patient"
        return "unknown"
