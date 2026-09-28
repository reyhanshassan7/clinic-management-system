from django.contrib import admin
from .models import (
    Role, Dept, Staff, Specialization, Doctor, Receptionist, 
    LabTechnician, Pharmacist, Patient, Appointment, Consultation, 
    Medicine, Prescription, PrescriptionItem, LabTest, LabOrder, 
    LabOrderItem, MedicalReport, Bill, Payment, LabBill
)

models_list = [
    Role, Dept, Staff, Specialization, Doctor, Receptionist, 
    LabTechnician, Pharmacist, Patient, Appointment, Consultation, 
    Medicine, Prescription, PrescriptionItem, LabTest, LabOrder, 
    LabOrderItem, MedicalReport, Bill, Payment, LabBill
]

admin.site.register(models_list)