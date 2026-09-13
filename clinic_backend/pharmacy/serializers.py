from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from api.models import Medicine, PrescriptionItem
from .models import MedicineDispense


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


class PrescriptionItemSerializer(serializers.ModelSerializer):
    """
    Read-only view of one line item inside a prescription — this is what
    the pharmacist looks at to decide what to dispense.
    """
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    medicine_stock = serializers.IntegerField(source='medicine.stock', read_only=True)
    expiry_date = serializers.DateField(source='medicine.expiry_date', read_only=True)
    already_dispensed = serializers.SerializerMethodField()
    remaining_quantity = serializers.SerializerMethodField()

    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'prescription', 'medicine', 'medicine_name', 'medicine_stock',
            'expiry_date', 'dosage', 'quantity', 'already_dispensed', 'remaining_quantity',
        ]

    def get_already_dispensed(self, obj):
        return obj.dispenses.aggregate(total=Sum('quantity_dispensed'))['total'] or 0

    def get_remaining_quantity(self, obj):
        return obj.quantity - self.get_already_dispensed(obj)


class MedicineDispenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineDispense
        fields = '__all__'
        read_only_fields = ['dispensed_at']

    def validate(self, data):
        item = data['prescription_item']
        medicine = item.medicine
        qty = data['quantity_dispensed']

        if qty <= 0:
            raise serializers.ValidationError(
                {"quantity_dispensed": "Quantity dispensed must be greater than zero."}
            )

        if medicine.expiry_date and medicine.expiry_date < timezone.now().date():
            raise serializers.ValidationError(
                {"prescription_item": f"{medicine.name} is expired and cannot be dispensed."}
            )

        if qty > medicine.stock:
            raise serializers.ValidationError(
                {"quantity_dispensed": "Not enough stock for this medicine."}
            )

        already_dispensed = item.dispenses.aggregate(
            total=Sum('quantity_dispensed')
        )['total'] or 0
        remaining = item.quantity - already_dispensed
        if qty > remaining:
            raise serializers.ValidationError(
                {"quantity_dispensed": f"Cannot dispense {qty}; only {remaining} left on this prescription."}
            )

        return data