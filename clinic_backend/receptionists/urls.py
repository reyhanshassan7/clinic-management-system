from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ReceptionistLoginView,
    PatientViewSet,
    DoctorViewSet,
    ReceptionistAppointmentViewSet,
    BillViewSet,
    PaymentViewSet,
)


router = DefaultRouter()

router.register(
    r'patients',
    PatientViewSet,
    basename='receptionist-patient'
)

router.register(
    r'doctors',
    DoctorViewSet,
    basename='receptionist-doctor'
)

router.register(
    r'appointments',
    ReceptionistAppointmentViewSet,
    basename='receptionist-appointment'
)

router.register(
    r'bills',
    BillViewSet,
    basename='receptionist-bill'
)

router.register(
    r'payments',
    PaymentViewSet,
    basename='receptionist-payment'
)


urlpatterns = [
    path(
        'login/',
        ReceptionistLoginView.as_view(),
        name='receptionist-login'
    ),

    path(
        '',
        include(router.urls)
    ),
]