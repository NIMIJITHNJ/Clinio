from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from patients.models import Patient



class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='appointments_as_doctor')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Cancelled', 'Cancelled')], default='Pending')
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=10, choices=[('online', 'Online'), ('offline', 'Offline')], default='online')
    payment_status = models.CharField(max_length=10, choices=[('unpaid', 'Unpaid'), ('paid', 'Paid')], default='unpaid')
    payment_method = models.CharField(max_length=10, choices=[('online', 'Online'), ('offline', 'Offline')], default='offline')
    amount = models.IntegerField(default=0)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def calculate_fee(self):
        if self.doctor.specialization == 'Cardiologist':
            return 800
        elif self.doctor.specialization == 'Neurologist':
            return 1000
        else:
            return 500

    def set_fee_if_not_set(self):
        if self.amount == 0:
            self.amount = self.calculate_fee()
            self.save()


    def __str__(self):
        return f"{self.patient.user.first_name} {self.patient.user.last_name} with {self.doctor.user.get_full_name} on {self.date}"


def get_available_slots(doctor, date):
    from doctors.models import DoctorAvailability
    try:
        availability = DoctorAvailability.objects.get(doctor=doctor, date=date)
        start = datetime.combine(date, availability.start_time)
        end = datetime.combine(date, availability.end_time)
        slot_duration = timedelta(minutes=30)
        slots = []

        while start + slot_duration <= end:
            slots.append(start.time().strftime("%H:%M"))
            start += slot_duration

        booked = Appointment.objects.filter(doctor=doctor, date=date).values_list('time', flat=True)
        return [s for s in slots if s not in [b.strftime("%H:%M") for b in booked]]
    except DoctorAvailability.DoesNotExist:
        return []

class Consultation(models.Model):
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE, related_name='consultation')
    symptoms = models.TextField("Patient Complaints / Symptoms")
    diagnosis = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    lab_referral = models.TextField("Lab Referral", blank=True, null=True)
    xray_referral = models.TextField("X-Ray / Scan Referral", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation for {self.appointment.patient.user.get_full_name()} on {self.appointment.date}"
