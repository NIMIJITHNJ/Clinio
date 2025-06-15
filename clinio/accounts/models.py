from django.db import models
from appointments.models import Appointment

class Bill(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='bill')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Bill for Appointment #{self.appointment.id}"
