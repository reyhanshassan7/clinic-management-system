from django.db import models
from api.models import PrescriptionItem, Pharmacist


class MedicineDispense(models.Model):
    prescription_item = models.ForeignKey(PrescriptionItem, on_delete=models.CASCADE, related_name='dispenses')
    pharmacist = models.ForeignKey(Pharmacist, on_delete=models.SET_NULL, null=True)
    quantity_dispensed = models.IntegerField()
    dispensed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prescription_item.medicine.name} x{self.quantity_dispensed}"