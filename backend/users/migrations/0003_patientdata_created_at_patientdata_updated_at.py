# Generated by Django 5.1.1 on 2024-10-01 09:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_patientdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientdata',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 1, 0, 0)),
        ),
        migrations.AddField(
            model_name='patientdata',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
