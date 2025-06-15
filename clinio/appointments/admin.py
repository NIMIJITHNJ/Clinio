from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'doctor_name', 'date', 'status']

    def patient_name(self, obj):
        return obj.patient.user.get_full_name() or obj.patient.user.username

    def doctor_name(self, obj):
        return obj.doctor.user.get_full_name() or obj.doctor.user.username
