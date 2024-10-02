# Generated by Django 5.1.1 on 2024-10-02 18:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_patientdata_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patientdata',
            name='blood_pressure',
        ),
        migrations.RemoveField(
            model_name='patientdata',
            name='user',
        ),
        migrations.RemoveField(
            model_name='patientdata',
            name='weight',
        ),
        migrations.AddField(
            model_name='patientdata',
            name='patient',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='vitals', to='users.patientprofile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patientdata',
            name='respiratory_rate',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='patientdata',
            name='spo2',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='patientdata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='patientdata',
            name='heart_rate',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='patientdata',
            name='temperature',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
    ]