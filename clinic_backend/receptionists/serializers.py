from rest_framework import serializers

from api.models import (
    Patient,
    Appointment,
    Doctor,
    Bill,
    Payment,
)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError(
                "Phone number must contain 10 to 15 digits."
            )

        return value


class DoctorSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(
        source='staff.full_name',
        read_only=True
    )

    specialization_name = serializers.CharField(
        source='specialization.name',
        read_only=True
    )

    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )

    class Meta:
        model = Doctor
        fields = [
            'id',
            'doctor_name',
            'specialization_name',
            'department_name',
            'consultation_fee',
            'qualification',
            'experience_years',
            'license_number',
            'is_active',
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source='patient.full_name',
        read_only=True
    )

    doctor_name = serializers.CharField(
        source='doctor.staff.full_name',
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'patient_name',
            'doctor',
            'doctor_name',
            'appointment_date',
            'status',
        ]

    def validate(self, attrs):
        doctor = attrs.get('doctor')

        if doctor and not doctor.is_active:
            raise serializers.ValidationError(
                "Selected doctor is inactive."
            )

        return attrs


class BillSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source='consultation.appointment.patient.full_name',
        read_only=True
    )

    doctor_name = serializers.CharField(
        source='consultation.appointment.doctor.staff.full_name',
        read_only=True
    )

    class Meta:
        model = Bill
        fields = [
            'id',
            'consultation',
            'patient_name',
            'doctor_name',
            'total_amount',
            'is_paid',
        ]


class PaymentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source='bill.consultation.appointment.patient.full_name',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'bill',
            'patient_name',
            'amount_paid',
            'payment_method',
            'payment_date',
        ]

        read_only_fields = [
            'payment_date'
        ]

    def validate_amount_paid(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Payment amount must be greater than zero."
            )

        return value