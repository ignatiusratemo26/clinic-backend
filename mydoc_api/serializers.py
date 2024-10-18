from rest_framework import serializers
from .models import Doctor, Appointment, AvailableTimeSlot, Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = Profile
        fields = ['username','email','wallet_balance']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        data['username'] = data['username'].lower()
        return data

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
