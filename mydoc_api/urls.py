from django.urls import path
from .views import DoctorViewSet, AppointmentViewSet, AvailableTimeSlotViewSet
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = router.urls
urlpatterns += [
    path('doctors/', DoctorViewSet.as_view({'get': 'list'}), name='doctor-list'),
    path('appointments/', AppointmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='appointment-list'),
    path('appointments/filter_by_status/', AppointmentViewSet.as_view({'get': 'filter_by_status'}), name='appointment-filter-by-status'),
    path('available_time_slots/', AvailableTimeSlotViewSet.as_view({'get': 'list'}), name='available-time-slot-list'),
]