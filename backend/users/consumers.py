import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from decimal import Decimal
from django.utils import timezone
from channels.exceptions import DenyConnection
from .models import DoctorData, PatientData,VitalHistoryPatient,VitalHistoryDoctor
from users.mqtt_client import setup_mqtt_client
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model
subject_group_mapping = {
    "Hardware Configuration": "hardware_group_",
    "Glucose": "glucose_group_",
    "Temperature": "temperature_group_",
    "Oximeter": "oximeter_group_"
}
User = get_user_model()

active_device_connections = {}

class VitalDataConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.device_id = None
        self.mqtt_client = None

    async def connect(self):
        token = self.scope['query_string'].decode().split('=')[-1]  # Extract token
        self.device_id = self.scope['query_string'].decode().split('&')[0].split('=')[-1]  # Extract device_id

        try:
            validated_token = await self.get_validated_token(token)
            self.user = await self.get_user_from_token(validated_token)

            if self.user.is_authenticated:
                self.role = await self.get_user_role()

                # Check if the device ID is already in use
                if self.device_id in active_device_connections:
                    # If the device is already in use, deny the connection
                    await self.send(text_data=json.dumps({'error': 'Device is busy'}))
                    raise DenyConnection("Device is already in use")
                
                # Register the new connection
                active_device_connections[self.device_id] = self.channel_name

                await self.accept()
                await self.send(text_data=json.dumps({'status': 'connected', 'user': str(self.user), 'role': self.role}))

                # Add the consumer to all subject groups based on the device_id
                for subject, group_prefix in subject_group_mapping.items():
                    group_name = f"{group_prefix}{self.device_id}"
                    await self.channel_layer.group_add(group_name, self.channel_name)

                # Set up the MQTT client with the dynamic device_id
                self.mqtt_client = setup_mqtt_client(self.device_id)

        except InvalidToken:
            await self.send(text_data=json.dumps({'error': 'Invalid token'}))
            await self.close()

    async def disconnect(self, close_code):
        if self.device_id:
            # Remove the connection from the active connections
            if self.device_id in active_device_connections:
                del active_device_connections[self.device_id]

            # Save the current vitals to the VitalHistory model
            await self.save_vitals_to_history()

            # Remove the consumer from all groups
            for subject, group_prefix in subject_group_mapping.items():
                group_name = f"{group_prefix}{self.device_id}"
                await self.channel_layer.group_discard(group_name, self.channel_name)




    async def receive(self, text_data):
        """Handle WebSocket messages for subscribing/publishing topics."""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("message")
     
        if message_type:
            
            # Publish the data to the dynamic MQTT topic based on device_id
            self.mqtt_client.publish(f"HK_Sub{self.device_id}", payload=message_type)
        else:
            await self.send(text_data=json.dumps({'error': 'Invalid message type'}))
    
    async def temperature_message(self, event):
        """Handle temperature messages received in the temperature group."""
        message = event['message']
        message_data = json.loads(message)

        status = message_data.get("Status")
        temperature = message_data.get("Temperature")

        if status and temperature:
            await self.send(text_data=json.dumps({'Status': status}))
            await self.save_temperature_to_db(temperature)
        else:
            await self.send(text_data=json.dumps(message_data))

    async def oximeter_message(self, event):
        """Handle temperature messages received in the temperature group."""
        message = event['message']
        message_data = json.loads(message)

        status = message_data.get("Status")
        heart_rate= message_data.get("Heart_Rate")
        spo2 = message_data.get("SPO2")

        if status and heart_rate and spo2:
            await self.send(text_data=json.dumps({'Status': status}))
            await self.save_oximeter_to_db(heart_rate,spo2)
        else:
            await self.send(text_data=json.dumps(message_data))
    
    async def hardware_message(self, event):
        """Handle temperature messages received in the temperature group."""
        message = event['message']
        message_data = json.loads(message)

        status = message_data.get("Status")
        # temperature = message_data.get("Temperature")

        # if status and temperature:
        await self.send(text_data=json.dumps({'Status': status}))
        #     await self.save_temperature_to_db(temperature)
        # else:
        # await self.send(text_data=json.dumps(m))
    
    async def glucose_message(self, event):
        """Handle temperature messages received in the temperature group."""
        message = event['message']
        message_data = json.loads(message)
        glucose=message_data['Glucose']
        samples=message_data['Samples']
        await self.send(text_data=json.dumps(message_data))
        await self.save_glucose_to_db(glucose,samples)


    @sync_to_async
    def save_temperature_to_db(self, temperature):
        """Save temperature data to the database based on the user role."""
        if self.role == 'doctor':
            doctor_profile = self.user.doctorprofile
            doctor_data, created = DoctorData.objects.get_or_create(
                doctor=doctor_profile,
                defaults={'temperature': Decimal(temperature), 'created_at': timezone.now()}
            )
            if not created:
                doctor_data.temperature = Decimal(temperature)
                doctor_data.save()
        elif self.role == 'patient':
            patient_profile = self.user.patientprofile
            patient_data, created = PatientData.objects.get_or_create(
                patient=patient_profile,
                defaults={'temperature': Decimal(temperature), 'created_at': timezone.now()}
            )
            if not created:
                patient_data.temperature = Decimal(temperature)
                patient_data.save()

    @sync_to_async
    def save_glucose_to_db(self, glucose_level, samples):
        """Save glucose level and samples data to the database."""
        if self.role == 'doctor':
            doctor_profile = self.user.doctorprofile
            doctor_data, created = DoctorData.objects.get_or_create(
                doctor=doctor_profile,
                defaults={'glucose_level': Decimal(glucose_level), 'glucose_samples': samples, 'created_at': timezone.now()}
            )
            if not created:
                doctor_data.glucose_level = Decimal(glucose_level)
                doctor_data.glucose_samples = samples  # Update the samples array
                doctor_data.save()
        elif self.role == 'patient':
            patient_profile = self.user.patientprofile
            patient_data, created = PatientData.objects.get_or_create(
                patient=patient_profile,
                defaults={'glucose_level': Decimal(glucose_level), 'glucose_samples': samples, 'created_at': timezone.now()}
            )
            if not created:
                patient_data.glucose_level = Decimal(glucose_level)
                patient_data.glucose_samples = samples  # Update the samples array
                patient_data.save()

    @sync_to_async
    def save_oximeter_to_db(self, heart_rate, spo2):
        """Save oximeter (heart rate and oxygen level) data to the database."""
        if self.role == 'doctor':
            doctor_profile = self.user.doctorprofile
            doctor_data, created = DoctorData.objects.get_or_create(
                doctor=doctor_profile,
                defaults={'heart_rate': Decimal(heart_rate), 'spo2': Decimal(spo2), 'created_at': timezone.now()}
            )
            if not created:
                doctor_data.heart_rate = Decimal(heart_rate)
                doctor_data.spo2 = Decimal(spo2)
                doctor_data.save()
        elif self.role == 'patient':
            patient_profile = self.user.patientprofile
            patient_data, created = PatientData.objects.get_or_create(
                patient=patient_profile,
                defaults={'heart_rate': Decimal(heart_rate), 'spo2': Decimal(spo2), 'created_at': timezone.now()}
            )
            if not created:
                patient_data.heart_rate = Decimal(heart_rate)
                patient_data.spo2 = Decimal(spo2)
                patient_data.save()
    @sync_to_async
    def save_vitals_to_history(self):
        """Save the current vitals to VitalHistory before disconnecting."""
        if self.role == 'doctor':
            doctor_profile = self.user.doctorprofile
            doctor_data = DoctorData.objects.filter(doctor=doctor_profile).latest('created_at')
            VitalHistoryDoctor.objects.create(
                doctor=doctor_profile,
                temperature=doctor_data.temperature,
                glucose_level=doctor_data.glucose_level,
                glucose_samples=doctor_data.glucose_samples,
                heart_rate=doctor_data.heart_rate,
                spo2=doctor_data.spo2,
            )
        elif self.role == 'patient':
            patient_profile = self.user.patientprofile
            patient_data = PatientData.objects.filter(patient=patient_profile).latest('created_at')
            VitalHistoryPatient.objects.create(
                patient=patient_profile,
                temperature=patient_data.temperature,
                glucose_level=patient_data.glucose_level,
                glucose_samples=patient_data.glucose_samples,
                heart_rate=patient_data.heart_rate,
                spo2=patient_data.spo2,
            )


    @sync_to_async
    def get_validated_token(self, token):
        return UntypedToken(token)

    @sync_to_async
    def get_user_from_token(self, validated_token):
        return User.objects.get(id=validated_token['user_id'])

    @sync_to_async
    def get_user_role(self):
        if hasattr(self.user, 'doctorprofile'):
            return "doctor"
        elif hasattr(self.user, 'patientprofile'):
            return "patient"
        return "unknown"
