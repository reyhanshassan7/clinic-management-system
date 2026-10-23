from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    MedicineViewSet, MedicineDispenseViewSet, PrescriptionItemViewSet,
    PrescriptionViewSet, PharmacistLoginView,
    StockRequestViewSet, AdminStockRequestViewSet,
)

router = DefaultRouter()
router.register('medicines', MedicineViewSet, basename='pharmacy-medicine')
router.register('dispenses', MedicineDispenseViewSet, basename='pharmacy-dispense')
router.register('prescription-items', PrescriptionItemViewSet, basename='pharmacy-prescription-item')
router.register('prescriptions', PrescriptionViewSet, basename='pharmacy-prescription')
router.register('stock-requests', StockRequestViewSet, basename='stock-request')
router.register('admin-stock-requests', AdminStockRequestViewSet, basename='admin-stock-request')

urlpatterns = router.urls + [
    path('login/', PharmacistLoginView.as_view(), name='pharmacist-login'),
]