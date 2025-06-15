from django import forms
from django.contrib.auth.models import User
from .models import Doctor
from .models import DoctorAvailability
from appointments.models import Consultation
from .models import LabReferral, XRayReferral

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['profile_pic', 'name', 'qualifications', 'department', 'specialization', 'phone']
        widgets = {
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'w-full border rounded p-2'}),
            'name': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'qualifications': forms.SelectMultiple(attrs={'class': 'w-full border rounded p-2'}),
            'department': forms.Select(attrs={'class': 'w-full border rounded p-2'}),
            'specialization': forms.Select(attrs={'class': 'w-full border rounded p-2'}),
            'phone': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
        }

class DoctorUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border rounded p-2'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
        }

class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailability
        fields = ['doctor', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.user.get_full_name()}"

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['symptoms', 'diagnosis', 'prescription', 'lab_referral', 'xray_referral']
        widgets = {
            'symptoms': forms.Textarea(attrs={'rows': 3}),
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'prescription': forms.Textarea(attrs={'rows': 3}),
            'lab_referral': forms.Textarea(attrs={'rows': 3}),
            'xray_referral': forms.Textarea(attrs={'rows': 3}),
        }

class LabReferralForm(forms.ModelForm):
    class Meta:
        model = LabReferral
        fields = ['report_file', 'description']

class XRayReferralForm(forms.ModelForm):
    class Meta:
        model = XRayReferral
        fields = ['image_file', 'description']