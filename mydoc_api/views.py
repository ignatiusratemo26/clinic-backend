from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters
from .models import Doctor, Appointment, AvailableTimeSlot, Profile
from .serializers import DoctorSerializer, AppointmentSerializer, AvailableTimeSlotSerializer, LoginSerializer, ProfileSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db import transaction


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def recharge_wallet(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = Decimal(amount)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = request.user.profile
        user_profile.wallet_balance += amount
        user_profile.save()
        return Response({'wallet_balance': user_profile.wallet_balance})


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

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Get appointment data
        available_time_slot_id = request.data.get('available_time_slot_id')

        # Find the available time slot
        available_time_slot = get_object_or_404(
            AvailableTimeSlot,
            id=available_time_slot_id,
            
            is_available=True,  # Ensure the time slot is available
            is_booked=False  # Ensure the time slot is not booked
        )
        doctor=available_time_slot.doctor
        consultation_fee=doctor.fee
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

        # Mark the time slot as booked
        available_time_slot.is_booked = True
        available_time_slot.is_available = False
        available_time_slot.save()

        # Create the appointment
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=available_time_slot.available_date,
            start_time=available_time_slot.start_time,
            end_time=available_time_slot.end_time,
            status='upcoming'
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
        elif doctor_id:
            return AvailableTimeSlot.objects.filter(doctor_id=doctor_id)
        return super().get_queryset()

    @action(detail=True, methods=['post'], url_path='book', url_name='book')
    def book_time_slot(self, request, pk=None):
        try:
            time_slot = self.get_object()
            if time_slot.is_booked:
                return Response({'error': 'Time slot is already booked.'}, status=status.HTTP_400_BAD_REQUEST)
            time_slot.is_booked = True
            time_slot.is_available = False
            time_slot.save()
            return Response({'message': 'Time slot booked successfully.'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Time slot not found.'}, status=status.HTTP_404_NOT_FOUND)
