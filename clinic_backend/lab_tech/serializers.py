from rest_framework import serializers
from api.models import LabTest, LabOrder, LabOrderItem, LabBill


class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = '__all__'


class LabOrderItemSerializer(serializers.ModelSerializer):
    lab_test_name = serializers.CharField(
        source='lab_test.name',
        read_only=True
    )

    class Meta:
        model = LabOrderItem
        fields = [
            'id',
            'lab_order',
            'lab_test',
            'lab_test_name',
            'result'
        ]


class LabOrderSerializer(serializers.ModelSerializer):
    items = LabOrderItemSerializer(
        source='laborderitem_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = LabOrder
        fields = [
            'id',
            'consultation',
            'technician',
            'status',
            'created_at',
            'items'
        ]


class LabBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabBill
        fields = '__all__'