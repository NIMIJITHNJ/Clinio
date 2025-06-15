from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from .models import Patient

class CustomUserCreationForm(UserCreationForm):
    agree_to_terms = forms.BooleanField(
        required=True,
        label="I agree to the terms & conditions",
        error_messages={'required': 'You must agree to the terms to register.'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'agree_to_terms']

class OnlinePatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300'
        }),
        required=False
    )
    first_name = forms.CharField(max_length=30, required=True, 
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg'
    }))
    last_name = forms.CharField(max_length=30, required=True, 
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg'
    }))

    class Meta:
        model = Patient
        fields = ['phone', 'gender', 'date_of_birth', 'address', 'city', 'state', 'zip_code']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'state': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'zip_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }
        
    def save(self, commit=True):
        patient = super().save(commit=False)
        user = patient.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            patient.save()
        return patient

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required for online registration.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class OfflinePatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300'
        }),
        required=False
    )
        
    class Meta:
        model = Patient
        fields = ['phone', 'gender', 'date_of_birth', 'address', 'city', 'state', 'zip_code']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border rounded-lg'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'state': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'zip_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already used.")
        return email

class ResetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class OfflinePatientUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
        }