from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Sum

from rest_framework import viewsets, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from api.models import (
    Patient,
    Appointment,
    Doctor,
    Bill,
    Payment,
    Staff,
)

from .serializers import (
    PatientSerializer,
    AppointmentSerializer,
    DoctorSerializer,
    BillSerializer,
    PaymentSerializer,
)

from .permissions import IsReceptionist


class ReceptionistLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {
                    'error': 'Username and password are required'
                },
                status=400
            )

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {
                    'error': 'Invalid username or password'
                },
                status=401
            )

        try:
            staff = Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            return Response(
                {
                    'error': 'Staff account not found'
                },
                status=403
            )

        if not staff.is_active:
            return Response(
                {
                    'error': 'Staff account is inactive'
                },
                status=403
            )

        if not staff.role or staff.role.role_name != 'Receptionist':
            return Response(
                {
                    'error': 'Only Receptionists can login here'
                },
                status=403
            )

        try:
            receptionist = staff.receptionist
        except Exception:
            return Response(
                {
                    'error': 'Receptionist profile not found'
                },
                status=403
            )

        if not receptionist.is_active:
            return Response(
                {
                    'error': 'Receptionist account is inactive'
                },
                status=403
            )

        token, created = Token.objects.get_or_create(
            user=user
        )

        return Response({
            'message': 'Receptionist login successful',
            'token': token.key,
            'username': user.username,
            'role': staff.role.role_name,
            'staff_id': staff.id,
            'receptionist_id': receptionist.id,
            'full_name': staff.full_name,
        })


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsReceptionist]

    def get_queryset(self):
        queryset = Patient.objects.all().order_by('id')

        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsReceptionist]

    def get_queryset(self):
        queryset = Doctor.objects.filter(
            is_active=True,
            staff__is_active=True
        ).select_related(
            'staff',
            'specialization',
            'department'
        )

        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                Q(staff__full_name__icontains=search) |
                Q(specialization__name__icontains=search) |
                Q(department__name__icontains=search)
            )

        return queryset


class ReceptionistAppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsReceptionist]

    def get_queryset(self):
        queryset = Appointment.objects.all().select_related(
            'patient',
            'doctor',
            'doctor__staff'
        ).order_by('-appointment_date')

        patient_id = self.request.query_params.get('patient')
        doctor_id = self.request.query_params.get('doctor')
        status = self.request.query_params.get('status')

        if patient_id:
            queryset = queryset.filter(
                patient_id=patient_id
            )

        if doctor_id:
            queryset = queryset.filter(
                doctor_id=doctor_id
            )

        if status:
            queryset = queryset.filter(
                status=status
            )

        return queryset


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [IsReceptionist]

    def get_queryset(self):
        queryset = Bill.objects.all().select_related(
            'consultation',
            'consultation__appointment',
            'consultation__appointment__patient',
            'consultation__appointment__doctor',
            'consultation__appointment__doctor__staff'
        ).order_by('-id')

        paid = self.request.query_params.get('paid')

        if paid == 'true':
            queryset = queryset.filter(is_paid=True)

        elif paid == 'false':
            queryset = queryset.filter(is_paid=False)

        return queryset


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsReceptionist]

    def get_queryset(self):
        return Payment.objects.all().select_related(
            'bill',
            'bill__consultation',
            'bill__consultation__appointment',
            'bill__consultation__appointment__patient'
        ).order_by('-payment_date')

    @transaction.atomic
    def perform_create(self, serializer):
        bill_id = self.request.data.get('bill')

        if not bill_id:
            raise serializers.ValidationError(
                {'bill': 'Bill is required.'}
            )

        try:
            bill = Bill.objects.select_for_update().get(
                id=bill_id
            )
        except Bill.DoesNotExist:
            raise serializers.ValidationError(
                {'bill': 'Bill not found.'}
            )

        previous_payments = Payment.objects.filter(
            bill=bill
        ).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0

        new_amount = serializer.validated_data['amount_paid']

        if previous_payments + new_amount > bill.total_amount:
            raise serializers.ValidationError(
                {
                    'amount_paid':
                    'Payment exceeds the remaining bill amount.'
                }
            )

        serializer.save()

        total_paid = previous_payments + new_amount

        if total_paid >= bill.total_amount:
            bill.is_paid = True
            bill.save(update_fields=['is_paid'])