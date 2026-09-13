from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet, MedicineDispenseViewSet, PrescriptionItemViewSet

router = DefaultRouter()
router.register('medicines', MedicineViewSet)
router.register('dispenses', MedicineDispenseViewSet)
router.register('prescription-items', PrescriptionItemViewSet)

urlpatterns = router.urls