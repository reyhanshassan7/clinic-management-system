from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet, MedicineDispenseViewSet

router = DefaultRouter()
router.register('medicines', MedicineViewSet)
router.register('dispenses', MedicineDispenseViewSet)

urlpatterns = router.urls