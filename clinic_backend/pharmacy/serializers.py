from rest_framework import serializers
from api.models import Medicine
from .models import MedicineDispense

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class MedicineDispenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineDispense
        fields = '__all__'
        read_only_fields = ['dispensed_at']

    def validate(self, data):
        medicine = data['prescription_item'].medicine
        if data['quantity_dispensed'] > medicine.stock:
            raise serializers.ValidationError("Not enough stock for this medicine.")
        return data