from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PatientViewSet,
    ReceptionistAppointmentViewSet,
    BillViewSet,
    PaymentViewSet,
)

router = DefaultRouter()

router.register(
    'patients',
    PatientViewSet,
    basename='patient'
)

router.register(
    'appointments',
    ReceptionistAppointmentViewSet,
    basename='receptionist-appointment'
)

router.register(
    'bills',
    BillViewSet,
    basename='bill'
)

router.register(
    'payments',
    PaymentViewSet,
    basename='payment'
)

urlpatterns = [
    path('', include(router.urls)),
]