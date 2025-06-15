from django import forms
from .models import Appointment
from patients.models import Patient
from doctors.models import Doctor
from django.contrib.auth.models import User

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']

class StaffAppointmentForm(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), label="Select Patient")
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), label="Select Doctor")

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'reason']

class AdminAppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        to_field_name='id',  # ensures dropdown uses Doctor.id
        label="Select Doctor"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']

class StaffEditAppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        to_field_name='id',  # ensures dropdown uses Doctor.id
        label="Select Doctor"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']