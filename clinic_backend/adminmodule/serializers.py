from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import date
import re

from api.models import Role, Dept, Staff, Medicine, LabTest, Doctor, Specialization


# ---------------- ROLE ----------------

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = '__all__'

    def validate_role_name(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Role name must contain at least 3 characters."
            )

        if not re.match(r'^[A-Za-z ]+$', value):
            raise serializers.ValidationError(
                "Role name should contain only alphabets and spaces."
            )

        return value


# ---------------- DEPARTMENT ----------------

class DeptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dept
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Department name must contain at least 3 characters."
            )

        if not re.match(r'^[A-Za-z ]+$', value):
            raise serializers.ValidationError(
                "Department name should contain only alphabets and spaces."
            )

        return value


# ---------------- STAFF ----------------

class StaffSerializer(serializers.ModelSerializer):

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        required=True
    )

    # ---- Doctor-only fields (role = Doctor na mattum fill pannanum) ----
    specialization = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(), write_only=True, required=False
    )
    consultation_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, required=False
    )
    qualification = serializers.CharField(write_only=True, required=False)
    experience_years = serializers.IntegerField(write_only=True, required=False)
    license_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Staff
        fields = [
            'id',
            'username',
            'password',
            'full_name',
            'gender',
            'dob',
            'phone',
            'email',
            'role',
            'dept',
            'is_active',
            'specialization',
            'consultation_fee',
            'qualification',
            'experience_years',
            'license_number',
        ]

    # ---------- existing validations (same as unga code) ----------

    def validate_username(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must contain at least 3 characters."
            )

        if not re.match(r'^[A-Za-z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username can contain only letters, numbers and underscore."
            )

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must contain at least 8 characters."
            )

        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return value

    def validate_full_name(self, value):
        if not value:
            raise serializers.ValidationError(
                "Full name is required."
            )

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Full name must contain at least 3 characters."
            )

        if not re.match(r'^[A-Za-z ]+$', value):
            raise serializers.ValidationError(
                "Full name should contain only alphabets and spaces."
            )

        return value

    def validate_gender(self, value):
        value = value.strip().capitalize()

        if value not in ['Male', 'Female', 'Other']:
            raise serializers.ValidationError(
                "Gender must be Male, Female or Other."
            )

        return value

    def validate_dob(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Date of birth cannot be a future date."
            )

        return value

    def validate_phone(self, value):
        value = value.strip()

        if not re.match(r'^[0-9]{10}$', value):
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        if Staff.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "Phone number already exists."
            )

        return value

    def validate_email(self, value):
        value = value.strip()

        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError(
                "Enter a valid email address."
            )

        return value

    def validate_role(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign an inactive role."
            )

        return value

    def validate_dept(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign an inactive department."
            )

        return value

    # ---------- NEW: whole-object check ----------
    # Role "Doctor" nu select panninaa, doctor fields kandippa venum
    def validate(self, data):
        role = data.get('role')
        if role and role.role_name == 'Doctor':
            required_doctor_fields = ['specialization', 'consultation_fee', 'qualification']
            missing = [f for f in required_doctor_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError(
                    f"For Doctor role, these fields are required: {', '.join(missing)}"
                )
        return data

    # ---------- Create Staff + User (+ Doctor if role=Doctor) ----------
    def create(self, validated_data):
        # Doctor-only fields ah mudhalla pop pannu (Staff model ku sonthama illa)
        specialization = validated_data.pop('specialization', None)
        consultation_fee = validated_data.pop('consultation_fee', None)
        qualification = validated_data.pop('qualification', None)
        experience_years = validated_data.pop('experience_years', 0)
        license_number = validated_data.pop('license_number', None)

        username = validated_data.pop('username')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        staff = Staff.objects.create(
            user=user,
            **validated_data
        )

        # role "Doctor" na, Doctor record um create pannu
        if staff.role and staff.role.role_name == 'Doctor':
            Doctor.objects.create(
                staff=staff,
                specialization=specialization,
                department=staff.dept,
                consultation_fee=consultation_fee,
                qualification=qualification,
                experience_years=experience_years or 0,
                license_number=license_number,
            )

        return staff

    # ---------- Update ----------
    def update(self, instance, validated_data):
        validated_data.pop('username', None)

        password = validated_data.pop('password', None)
        if password:
            instance.user.set_password(password)
            instance.user.save()

        for attr in ['specialization', 'consultation_fee', 'qualification',
                     'experience_years', 'license_number']:
            validated_data.pop(attr, None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

#--------------SPECIALIZATION---------------


class SpecializationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specialization
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Specialization name must contain at least 2 characters."
            )

        return value

# ---------------- MEDICINE ----------------

class MedicineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicine
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Medicine name must contain at least 2 characters."
            )

        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative."
            )

        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Price cannot be negative."
            )

        return value


# ---------------- LAB TEST ----------------

class LabTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LabTest
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "Lab test name must contain at least 2 characters."
            )

        return value

    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Lab test cost cannot be negative."
            )

        return value