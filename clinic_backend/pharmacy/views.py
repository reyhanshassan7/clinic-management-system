from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.models import Medicine, PrescriptionItem
from .models import MedicineDispense
from .serializers import MedicineSerializer, MedicineDispenseSerializer, PrescriptionItemSerializer


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer


class PrescriptionItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only on purpose: creating/editing a prescription line item is the
    Doctor module's job, not the Pharmacist's. You only need to look at these.
    """
    queryset = PrescriptionItem.objects.select_related('medicine', 'prescription').all()
    serializer_class = PrescriptionItemSerializer


class MedicineDispenseViewSet(viewsets.ModelViewSet):
    queryset = MedicineDispense.objects.all()
    serializer_class = MedicineDispenseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = serializer.validated_data['prescription_item']
        qty = serializer.validated_data['quantity_dispensed']

        with transaction.atomic():
            # Lock this Medicine row until the transaction ends, so a second
            # request can't read the same "old" stock number at the same time.
            medicine = Medicine.objects.select_for_update().get(pk=item.medicine_id)

            if qty > medicine.stock:
                return Response(
                    {"quantity_dispensed": "Not enough stock for this medicine."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            medicine.stock -= qty
            medicine.save(update_fields=['stock'])
            self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)