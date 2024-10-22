from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from users.models import Sensor, SensorMeasurement

# Signal when a new Sensor is created
@receiver(post_save, sender=Sensor)
def sensor_created(sender, instance, created, **kwargs):
    if created:
        # Notify WebSocket group when a sensor is created
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{instance.sensor_id}",
            {
                "type": "sensor.created",
                "sensor_id": instance.sensor_id,
                "name": instance.name,
            }
        )

# Signal when a new SensorMeasurement is created
@receiver(post_save, sender=SensorMeasurement)
def sensor_measurement_created(sender, instance, created, **kwargs):
    if created:
        # Notify WebSocket group when a measurement is created
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{instance.sensor.sensor_id}",
            {
                "type": "measurement.created",
                "sensor_id": instance.sensor.sensor_id,
                "value": instance.value,
                "timestamp": instance.timestamp.isoformat(),
            }
        )

# Signal when a Sensor is deleted
@receiver(pre_delete, sender=Sensor)
def sensor_deleted(sender, instance, **kwargs):
    # Notify WebSocket group when a sensor is deleted
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"{instance.sensor_id}",
        {
            "type": "sensor.deleted",
            "sensor_id": instance.sensor_id,
        }
    )
