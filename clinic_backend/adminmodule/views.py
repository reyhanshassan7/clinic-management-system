from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from api.models import Role, Dept, Staff, Medicine, LabTest,Specialization
from .serializers import (
    RoleSerializer, DeptSerializer, StaffSerializer,
    MedicineSerializer, LabTestSerializer,SpecializationSerializer
)
from .permissions import IsAdmin


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]


class DeptViewSet(viewsets.ModelViewSet):
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    permission_classes = [IsAdmin]


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdmin]


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAdmin]


class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    permission_classes = [IsAdmin]




class SpecializationViewSet(viewsets.ModelViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [IsAdmin]


class ChangePasswordView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        user = request.user

        if not user.check_password(old_password):
            return Response({'error': 'Old password wrong'}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'})


class AdminLoginViewSet(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):

        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=400
            )

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {'error': 'Invalid username or password'},
                status=401
            )

        try:
            staff = Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            return Response(
                {'error': 'Staff account not found'},
                status=403
            )

        if not staff.is_active:
            return Response(
                {'error': 'Staff account is inactive'},
                status=403
            )

        if not staff.role or staff.role.role_name != 'Admin':
            return Response(
                {'error': 'Only Admin can login here'},
                status=403
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Admin login successful',
            'token': token.key,
            'username': user.username,
            'role': staff.role.role_name,
            'staff_id': staff.id
        })
