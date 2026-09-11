from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True) # Admin, Doctor, Receptionist, LabTech, Pharmacist

class Dept(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    dept = models.ForeignKey(Dept, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=15)

class Specialization(models.Model):
    name = models.CharField(max_length=100)

class Doctor(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    license_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

class Receptionist(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)

class LabTechnician(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)

class Pharmacist(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)

class Patient(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=15)
    blood_group = models.CharField(
        max_length=5,
        blank=True,
        null=True
    )

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, default='Scheduled')

class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    notes = models.TextField()

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    pharmacist = models.ForeignKey(Pharmacist, on_delete=models.SET_NULL, null=True, blank=True)

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)
    quantity = models.IntegerField()

class LabTest(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=8, decimal_places=2)

class LabOrder(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    technician = models.ForeignKey(LabTechnician, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class LabOrderItem(models.Model):
    lab_order = models.ForeignKey(LabOrder, on_delete=models.CASCADE)
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    result = models.TextField(blank=True, null=True)

class MedicalReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    report_details = models.TextField()

class Bill(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

class Payment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now_add=True)