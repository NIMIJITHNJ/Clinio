from django.contrib import admin
from .models import DoctorAvailability
from .forms import DoctorAvailabilityForm

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    form = DoctorAvailabilityForm
    list_display = ['doctor', 'date', 'start_time', 'end_time']
