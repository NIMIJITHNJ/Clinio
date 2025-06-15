from django import forms
from django.contrib.auth.models import User
from .models import Staff, StaffRole

class StaffUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border rounded p-2'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
        }


class StaffForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=StaffRole.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Staff
        fields = ['profile_pic', 'name', 'roles', 'phone']
        widgets = {
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'w-full border rounded p-2'}),
            'name': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'phone': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
        }
