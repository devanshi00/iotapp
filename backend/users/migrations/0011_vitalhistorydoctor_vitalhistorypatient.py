# Generated by Django 5.1.2 on 2024-10-24 09:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_doctordata_glucose_level_doctordata_glucose_samples_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VitalHistoryDoctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('glucose_level', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('glucose_samples', models.JSONField(blank=True, null=True)),
                ('oxygen_level', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('heart_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('spo2', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vital_history', to='users.doctorprofile')),
            ],
        ),
        migrations.CreateModel(
            name='VitalHistoryPatient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('glucose_level', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('glucose_samples', models.JSONField(blank=True, null=True)),
                ('oxygen_level', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('heart_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('spo2', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vital_history', to='users.patientprofile')),
            ],
        ),
    ]
