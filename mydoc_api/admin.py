from django.contrib import admin
from .models import Doctor, Appointment, AvailableTimeSlot, Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_balance')

# Register Doctor model
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'specialization', 'rating', 'fee')
    search_fields = ('first_name', 'last_name', 'specialization')
    list_filter = ('specialization',)

# Register Appointment model
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'appointment_date', 'start_time', 'end_time', 'status')
    search_fields = ('doctor__name', 'patient__username')
    list_filter = ('status', 'appointment_date')
    date_hierarchy = 'appointment_date'

# Register AvailableTimeSlot model
@admin.register(AvailableTimeSlot)
class AvailableTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'available_date', 'start_time', 'end_time', 'is_available', 'is_booked')
    search_fields = ('doctor__name',)
    list_filter = ('available_date', 'is_available', 'is_booked')
    date_hierarchy = 'available_date'
