from rest_framework import serializers
from .models import Doctor, Appointment, AvailableTimeSlot

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'first_name', 'last_name', 'specialization', 'profile_picture', 'rating', 'fee']

class AvailableTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTimeSlot
        fields = ['id', 'doctor', 'available_date', 'start_time', 'end_time', 'is_available']

class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'appointment_date', 'start_time', 'end_time', 'status']
