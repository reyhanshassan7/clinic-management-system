from rest_framework.routers import DefaultRouter

from .views import (
    LabTestViewSet,
    LabOrderViewSet,
    LabOrderItemViewSet,
    LabBillViewSet
)


router = DefaultRouter()

router.register(r'tests', LabTestViewSet, basename='lab-test')
router.register(r'orders', LabOrderViewSet, basename='lab-order')
router.register(r'order-items', LabOrderItemViewSet, basename='lab-order-item')
router.register(r'bills', LabBillViewSet, basename='lab-bill')

urlpatterns = router.urls