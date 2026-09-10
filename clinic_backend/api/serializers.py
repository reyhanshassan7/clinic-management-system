from rest_framework import serializers
from .models import Doctor, Appointment, Consultation, LabOrder, Prescription
from .models import LabOrder, Prescription

class LabOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabOrder
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'