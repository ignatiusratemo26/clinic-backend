from django.urls import path
from .views import DoctorViewSet, AppointmentViewSet, AvailableTimeSlotViewSet, ProfileViewSet
from rest_framework import routers
from .views import LoginView

router = routers.DefaultRouter()
urlpatterns = router.urls
urlpatterns += [
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileViewSet.as_view({'get': 'list', }) ),
    path('profile/recharge_wallet/', ProfileViewSet.as_view({'post': 'recharge_wallet'}), name='recharge-wallet'),
    path('doctors/', DoctorViewSet.as_view({'get': 'list'}), name='doctor-list'),
    path('appointments/', AppointmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='appointment-list'),
    path('appointments/filter_by_status/', AppointmentViewSet.as_view({'get': 'filter_by_status'}), name='appointment-filter-by-status'),
    path('available_time_slots/', AvailableTimeSlotViewSet.as_view({'get': 'list'}), name='available-time-slot-list'),
]