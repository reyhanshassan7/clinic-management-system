from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    MedicineViewSet, MedicineDispenseViewSet, PrescriptionItemViewSet,
    PrescriptionViewSet, PharmacistLoginView,
)

router = DefaultRouter()
router.register('medicines', MedicineViewSet, basename='pharmacy-medicine')
router.register('dispenses', MedicineDispenseViewSet, basename='pharmacy-dispense')
router.register('prescription-items', PrescriptionItemViewSet, basename='pharmacy-prescription-item')
router.register('prescriptions', PrescriptionViewSet, basename='pharmacy-prescription')

urlpatterns = router.urls + [
    path('login/', PharmacistLoginView.as_view(), name='pharmacist-login'),
]