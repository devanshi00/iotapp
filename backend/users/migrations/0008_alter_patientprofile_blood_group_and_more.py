# Generated by Django 5.0.3 on 2024-09-25 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_patientprofile_height_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientprofile',
            name='blood_group',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='patientprofile',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='patientprofile',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='patientprofile',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='patientprofile',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]