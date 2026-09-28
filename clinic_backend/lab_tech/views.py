from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from api.models import LabTest, LabOrder, LabOrderItem, LabBill
from .serializers import (
    LabTestSerializer,
    LabOrderSerializer,
    LabOrderItemSerializer,
    LabBillSerializer
)


class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer


class LabOrderViewSet(viewsets.ModelViewSet):
    queryset = LabOrder.objects.all()
    serializer_class = LabOrderSerializer


class LabOrderItemViewSet(viewsets.ModelViewSet):
    queryset = LabOrderItem.objects.all()
    serializer_class = LabOrderItemSerializer


class LabBillViewSet(viewsets.ModelViewSet):
    queryset = LabBill.objects.all()
    serializer_class = LabBillSerializer