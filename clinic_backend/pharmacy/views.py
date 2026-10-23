from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Medicine, Prescription, PrescriptionItem, Staff
from .models import MedicineDispense, StockRequest
from .permissions import IsPharmacist, IsAdminOrPharmacist, IsAdmin
from .serializers import (
    MedicineSerializer, MedicineDispenseSerializer, PrescriptionItemSerializer,
    PharmacyPrescriptionSerializer, StockRequestSerializer,
)


class PharmacistLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(username=request.data.get('username'),
                            password=request.data.get('password'))
        if user is None:
            return Response({'error': 'Invalid username or password'}, status=401)

        staff = Staff.objects.filter(user=user, is_active=True).select_related('role').first()
        pharmacist = getattr(staff, 'pharmacist', None) if staff else None
        if (not pharmacist or not pharmacist.is_active
                or not staff.role or staff.role.role_name != 'Pharmacist'):
            return Response({'error': 'Only an active pharmacist can log in here'}, status=403)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'pharmacist_id': pharmacist.id,
                         'name': staff.full_name})


class MedicineViewSet(viewsets.ReadOnlyModelViewSet):
    """Pharmacist can only view stock. Admin owns create/edit/delete."""
    queryset = Medicine.objects.filter(is_active=True)
    serializer_class = MedicineSerializer
    permission_classes = [IsAdminOrPharmacist]


class PrescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PharmacyPrescriptionSerializer
    permission_classes = [IsAdminOrPharmacist]

    def get_queryset(self):
        qs = Prescription.objects.select_related(
            'consultation__appointment__patient'
        ).prefetch_related('prescriptionitem_set__medicine')
        name = self.request.query_params.get('patient')
        if name:
            qs = qs.filter(consultation__appointment__patient__full_name__icontains=name)
        return qs.order_by('-id')


class PrescriptionItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only: creating prescription lines is the Doctor module's job."""
    queryset = PrescriptionItem.objects.select_related('medicine', 'prescription').all()
    serializer_class = PrescriptionItemSerializer
    permission_classes = [IsAdminOrPharmacist]


class MedicineDispenseViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                              mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = MedicineDispense.objects.select_related(
        'prescription_item__medicine', 'pharmacist__staff'
    ).order_by('-id')
    serializer_class = MedicineDispenseSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsPharmacist()]
        return [IsAdminOrPharmacist()]

    def create(self, request, *args, **kwargs):
        pharmacist = getattr(request.user.staff, 'pharmacist', None)
        if not pharmacist or not pharmacist.is_active:
            return Response({'detail': 'No active pharmacist profile.'}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.validated_data['prescription_item']
        qty = serializer.validated_data['quantity_dispensed']

        with transaction.atomic():
            # lock the medicine row so two requests can't use the same stock number
            medicine = Medicine.objects.select_for_update().get(pk=item.medicine_id)
            done = item.dispenses.aggregate(t=Sum('quantity_dispensed'))['t'] or 0

            if qty > medicine.stock:
                return Response({'quantity_dispensed': 'Not enough stock.'}, status=400)
            if qty > item.quantity - done:
                return Response({'quantity_dispensed': 'Exceeds prescribed quantity.'}, status=400)

            medicine.stock -= qty
            medicine.save(update_fields=['stock'])
            serializer.save(pharmacist=pharmacist)
            Prescription.objects.filter(
                pk=item.prescription_id, pharmacist__isnull=True
            ).update(pharmacist=pharmacist)

        return Response(serializer.data, status=201)

class StockRequestViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Pharmacist: ask the admin for more stock and see own requests."""
    serializer_class = StockRequestSerializer
    permission_classes = [IsPharmacist]

    def get_queryset(self):
        return (StockRequest.objects
                .filter(requested_by=self.request.user.staff.pharmacist)
                .select_related('medicine').order_by('-id'))

    def perform_create(self, serializer):
        medicine = serializer.validated_data['medicine']
        with transaction.atomic():
            # lock so a double click can't create two pending requests
            Medicine.objects.select_for_update().get(pk=medicine.pk)
            if StockRequest.objects.filter(medicine=medicine, status='Pending').exists():
                raise ValidationError({'medicine': 'A pending request already exists.'})
            serializer.save(requested_by=self.request.user.staff.pharmacist)


class AdminStockRequestViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    """Admin: receive stock by approving, or reject a request."""
    serializer_class = StockRequestSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = StockRequest.objects.select_related('medicine').order_by('-id')
        status_param = self.request.query_params.get('status')
        return qs.filter(status=status_param) if status_param else qs

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        try:
            qty = int(request.data.get('approved_quantity') or 0)
        except (TypeError, ValueError):
            return Response({'error': 'approved_quantity must be a number'}, status=400)

        with transaction.atomic():
            sr = get_object_or_404(StockRequest.objects.select_for_update(), pk=pk)
            if sr.status != 'Pending':
                return Response({'error': 'Request already resolved'}, status=400)
            qty = qty or sr.quantity          # default: approve what was asked
            if qty <= 0:
                return Response({'error': 'Quantity must be greater than zero'}, status=400)

            medicine = Medicine.objects.select_for_update().get(pk=sr.medicine_id)
            medicine.stock += qty
            medicine.save(update_fields=['stock'])

            sr.status = 'Approved'
            sr.approved_quantity = qty
            sr.remarks = request.data.get('remarks', '')
            sr.resolved_at = timezone.now()
            sr.resolved_by = request.user.staff
            sr.save()
        return Response(self.get_serializer(sr).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        with transaction.atomic():
            sr = get_object_or_404(StockRequest.objects.select_for_update(), pk=pk)
            if sr.status != 'Pending':
                return Response({'error': 'Request already resolved'}, status=400)
            sr.status = 'Rejected'
            sr.remarks = request.data.get('remarks', '')
            sr.resolved_at = timezone.now()
            sr.resolved_by = request.user.staff
            sr.save()
        return Response(self.get_serializer(sr).data)