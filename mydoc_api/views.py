from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters
from .models import Doctor, Appointment, AvailableTimeSlot
from .serializers import DoctorSerializer, AppointmentSerializer, AvailableTimeSlotSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
from django.shortcuts import get_object_or_404

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Use the LoginSerializer to validate the input
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Authenticate using username and password
        user = authenticate(username=username, password=password)
        if user:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Return the serializer for DRF browsable API form display
        serializer = LoginSerializer()
        return Response(serializer.data)

# ViewSet for managing Doctors
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'specialization']
    permission_classes = [AllowAny]




class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['doctor__first_name', 'doctor__last_name', 'doctor__specialization']

    def create(self, request, *args, **kwargs):
        # Get appointment data
        data = request.data
        doctor_id = data.get('doctor_id')
        doctor = get_object_or_404(Doctor, id=doctor_id)
        consultation_fee = doctor.consultation_fee  # Assume doctor has a fee

        available_time_slot = AvailableTimeSlot.objects.get(
            doctor=doctor,
            available_date=data.get('available_date'),
            start_time=data.get('start_time'),
            is_available=True
        )

        # Check if the user has enough balance
        user_profile = request.user.profile
        if user_profile.wallet_balance < consultation_fee:
            return Response(
                {'error': 'Insufficient balance in wallet.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct consultation fee from wallet
        user_profile.wallet_balance -= consultation_fee
        user_profile.save()

        # Book the time slot and create appointment
        available_time_slot.is_booked = True
        available_time_slot.save()

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=data.get('available_date'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time')
        )

        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def filter_by_status(self, request):
        status_param = request.query_params.get('status', None)
        if status_param:
            appointments = Appointment.objects.filter(patient=request.user, status=status_param)
            serializer = self.get_serializer(appointments, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# ViewSet for Available Time Slots
class AvailableTimeSlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AvailableTimeSlot.objects.all()
    serializer_class = AvailableTimeSlotSerializer

    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor_id')
        date = self.request.query_params.get('date')

        # Filter time slots based on doctor and date
        if doctor_id and date:
            return AvailableTimeSlot.objects.filter(doctor_id=doctor_id, available_date=date, is_available=True)
        return super().get_queryset()
    
    
