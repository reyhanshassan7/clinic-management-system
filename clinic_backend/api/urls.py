from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, AppointmentViewSet, ConsultationViewSet,LabOrderViewSet,PrescriptionViewSet,LoginViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'consultations', ConsultationViewSet)
router.register(r'lab-orders', LabOrderViewSet)
router.register(r'prescriptions', PrescriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginViewSet.as_view(), name='login'),
]