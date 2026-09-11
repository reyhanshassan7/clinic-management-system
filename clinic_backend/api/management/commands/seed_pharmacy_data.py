"""
Management command to seed test data for the pharmacist module.

Usage (from the clinic_backend folder, where manage.py lives):
    python manage.py seed_pharmacy_data

This creates one full chain:
    User -> Staff -> Pharmacist
    Patient
    User -> Staff -> Doctor
    Appointment -> Consultation -> Prescription -> PrescriptionItem
    Medicine

so you have a real PrescriptionItem to dispense against.

Place this file at:
    api/management/commands/seed_pharmacy_data.py

(Create the folders `management/` and `management/commands/` inside `api/`
if they don't exist, each with an empty `__init__.py` file.)
"""

from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import (
    Role, Dept, Staff, Specialization, Doctor,
    Patient, Appointment, Consultation, Medicine,
    Prescription, PrescriptionItem,
)
from api.models import Pharmacist


class Command(BaseCommand):
    help = "Seed sample data for testing the pharmacist dispense flow"

    def handle(self, *args, **options):
        # --- Roles & Dept ---
        pharmacist_role, _ = Role.objects.get_or_create(name="Pharmacist")
        doctor_role, _ = Role.objects.get_or_create(name="Doctor")
        pharmacy_dept, _ = Dept.objects.get_or_create(
            name="Pharmacy", defaults={"description": "Pharmacy department"}
        )
        general_dept, _ = Dept.objects.get_or_create(
            name="General Medicine", defaults={"description": "General medicine department"}
        )

        # --- Pharmacist chain: User -> Staff -> Pharmacist ---
        pharmacist_user, created = User.objects.get_or_create(
            username="test_pharmacist",
            defaults={"first_name": "Priya", "last_name": "Nair", "email": "priya@example.com"},
        )
        if created:
            pharmacist_user.set_password("testpass123")
            pharmacist_user.save()

        pharmacist_staff, _ = Staff.objects.get_or_create(
            user=pharmacist_user,
            defaults={"role": pharmacist_role, "dept": pharmacy_dept, "phone": "9999900001"},
        )
        pharmacist, _ = Pharmacist.objects.get_or_create(staff=pharmacist_staff)

        # --- Doctor chain: User -> Staff -> Doctor ---
        doctor_user, created = User.objects.get_or_create(
            username="test_doctor",
            defaults={"first_name": "Anil", "last_name": "Kumar", "email": "anil@example.com"},
        )
        if created:
            doctor_user.set_password("testpass123")
            doctor_user.save()

        doctor_staff, _ = Staff.objects.get_or_create(
            user=doctor_user,
            defaults={"role": doctor_role, "dept": general_dept, "phone": "9999900002"},
        )
        specialization, _ = Specialization.objects.get_or_create(name="General Medicine")
        doctor, _ = Doctor.objects.get_or_create(
            staff=doctor_staff, defaults={"specialization": specialization}
        )

        # --- Patient (no login user needed) ---
        patient, _ = Patient.objects.get_or_create(
            phone="9999900003",
            defaults={
                "address": "123 Test Street, Kerala",
                "date_of_birth": date(1995, 6, 15),
            },
        )

        # --- Appointment -> Consultation -> Prescription -> PrescriptionItem ---
        appointment, _ = Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            defaults={
                "appointment_date": timezone.now() + timedelta(days=0),
                "status": "Completed",
            },
        )
        consultation, _ = Consultation.objects.get_or_create(
            appointment=appointment,
            defaults={"diagnosis": "Mild fever", "notes": "Prescribed paracetamol, rest advised"},
        )
        prescription, _ = Prescription.objects.get_or_create(consultation=consultation)

        # --- Medicine ---
        medicine, _ = Medicine.objects.get_or_create(
            name="Paracetamol 500mg",
            defaults={"stock": 100, "price": 2.50},
        )

        prescription_item, created = PrescriptionItem.objects.get_or_create(
            prescription=prescription,
            medicine=medicine,
            defaults={"dosage": "1 tablet twice a day", "quantity": 10},
        )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully:"))
        self.stdout.write(f"  Pharmacist ID: {pharmacist.id} (user: {pharmacist_user.username})")
        self.stdout.write(f"  Doctor ID: {doctor.id} (user: {doctor_user.username})")
        self.stdout.write(f"  Patient ID: {patient.id}")
        self.stdout.write(f"  Medicine ID: {medicine.id} (stock: {medicine.stock})")
        self.stdout.write(f"  Prescription ID: {prescription.id}")
        self.stdout.write(f"  PrescriptionItem ID: {prescription_item.id}  <-- use this to test dispensing")
