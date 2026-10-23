from django.db import models
from api.models import PrescriptionItem, Pharmacist, Medicine, Staff


class MedicineDispense(models.Model):
    prescription_item = models.ForeignKey(PrescriptionItem, on_delete=models.CASCADE, related_name='dispenses')
    pharmacist = models.ForeignKey(Pharmacist, on_delete=models.SET_NULL, null=True)
    quantity_dispensed = models.IntegerField()
    dispensed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prescription_item.medicine.name} x{self.quantity_dispensed}"


class MedicineDispenseProxy(MedicineDispense):
    class Meta:
        proxy = True
        app_label = 'api'
        verbose_name = 'Medicine dispense'
        verbose_name_plural = 'Medicine dispenses'


class StockRequest(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_requests')
    requested_by = models.ForeignKey(Pharmacist, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    approved_quantity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def __str__(self):
        return f"{self.medicine.name} x{self.quantity} ({self.status})"