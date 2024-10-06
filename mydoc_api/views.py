from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from mydoc_api.authentication import FirebaseAuthentication
from rest_framework import filters
from .models import Doctor, Appointment, AvailableTimeSlot
from .serializers import DoctorSerializer, AppointmentSerializer, AvailableTimeSlotSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

# ViewSet for managing Doctors
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'specialization']
    permission_classes = [AllowAny]
    authentication_classes = [FirebaseAuthentication]


# ViewSet for Appointments
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseAuthentication]
    filter_backends = [filters.SearchFilter]
    search_fields = ['doctor__first_name', 'doctor__last_name', 'doctor__specialization']


    def create(self, request, *args, **kwargs):
        # Book an appointment
        data = request.data
        doctor_id = data.get('doctor_id')
        doctor = Doctor.objects.get(id=doctor_id)
        available_time_slot = AvailableTimeSlot.objects.get(
            doctor=doctor,
            available_date=data.get('available_date'),
            start_time=data.get('start_time'),
            is_available=True
        )

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

    # Filter Appointments by Status (complete, upcoming, cancelled)
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
    authentication_classes = [FirebaseAuthentication]

    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor_id')
        date = self.request.query_params.get('date')

        # Filter time slots based on doctor and date
        if doctor_id and date:
            return AvailableTimeSlot.objects.filter(doctor_id=doctor_id, available_date=date, is_available=True)
        return super().get_queryset()
    
    
