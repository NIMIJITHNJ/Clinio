from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from appointments.models import Consultation
from patients.models import Patient
from django.urls import reverse

DEPARTMENT_CHOICES = [
    ('General Medicine', 'General Medicine'),
    ('Cardiology', 'Cardiology'),
    ('Orthopaedics', 'Orthopaedics'),
    ('Neurology', 'Neurology'),
    ('Pediatrics', 'Pediatrics'),
    ('Dermatology', 'Dermatology'),
]

SPECIALIZATION_CHOICES = [
    ('General Physician', 'General Physician'),
    ('Cardiologist', 'Cardiologist'),
    ('Orthopaedist', 'Orthopaedist'),
    ('Neurologist', 'Neurologist'),
    ('Pediatrician', 'Pediatrician'),
    ('Dermatologist', 'Dermatologist'),
]

QUALIFICATION_CHOICES = [
    ('MBBS', 'MBBS'),
    ('MD', 'MD'),
    ('MS', 'MS'),
    ('DM', 'DM'),
    ('MCH', 'MCH'),
    ('BDS', 'BDS'),
    ('MDS', 'MDS'),
]

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='doctor_profiles/', null=True, blank=True)
    name = models.CharField(max_length=100)
    qualifications = MultiSelectField(choices=QUALIFICATION_CHOICES)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    phone = models.CharField(max_length=20)
    must_reset_password = models.BooleanField(default=True) 

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['doctor', 'date', 'start_time']

    def clean(self):
        # Check start < end
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

        # Check for overlaps
        existing = DoctorAvailability.objects.filter(
            doctor=self.doctor,
            date=self.date
        ).exclude(id=self.id)

        for slot in existing:
            if (self.start_time < slot.end_time and self.end_time > slot.start_time):
                raise ValidationError(f"Overlaps with existing slot: {slot.start_time} - {slot.end_time}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor} | {self.date} | {self.start_time} - {self.end_time}"

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)  
    consultation = models.OneToOneField('appointments.Consultation', on_delete=models.CASCADE, null=True, blank=True, related_name='linked_prescription')
    date = models.DateField(auto_now_add=True)
    details = models.TextField()

    def get_pdf_url(self):
        return reverse('print_prescription', args=[self.consultation.id])
    
    def __str__(self):
        return f"Prescription for {self.patient} on {self.date}"


class LabReferral(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    report_file = models.FileField(upload_to='lab_reports/')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Lab Report - {self.patient} - {self.date}"
    
    def get_pdf_url(self):
        return self.report_file.url

class XRayReferral(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    image_file = models.ImageField(upload_to='xray_reports/')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"X-Ray Report - {self.patient} - {self.date}"
    
    def get_pdf_url(self):
        return self.image_file.url