from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet, DeptViewSet, StaffViewSet,
    MedicineViewSet, LabTestViewSet, ChangePasswordView,SpecializationViewSet
)

router = DefaultRouter()
router.register('roles', RoleViewSet)
router.register('departments', DeptViewSet)
router.register('staff', StaffViewSet)
router.register('medicines', MedicineViewSet)
router.register('labtests', LabTestViewSet)
router.register('specializations', SpecializationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
   
]