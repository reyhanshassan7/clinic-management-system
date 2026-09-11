from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models import Medicine
from .models import MedicineDispense
from .serializers import MedicineSerializer, MedicineDispenseSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer

class MedicineDispenseViewSet(viewsets.ModelViewSet):
    queryset = MedicineDispense.objects.all()
    serializer_class = MedicineDispenseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            item = serializer.validated_data['prescription_item']
            qty = serializer.validated_data['quantity_dispensed']
            item.medicine.stock -= qty
            item.medicine.save()
            self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)