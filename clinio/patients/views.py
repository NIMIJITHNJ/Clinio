from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from .tasks import send_otp_email
import random
from django.contrib.auth.decorators import login_required
from .forms import ResetPasswordForm
from django.contrib.auth import update_session_auth_hash
from .models import Patient
from .forms import OnlinePatientForm
from doctors.models import Doctor
from appointments.models import Appointment
from patients.forms import OfflinePatientForm, OfflinePatientUserForm
from datetime import date




def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')  # Capture the checkbox value

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if not hasattr(user, 'patient'):
                Patient.objects.create(user=user, registered_by='online')

            # Handle "Remember Me" functionality
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks (in seconds)
            else:
                request.session.set_expiry(0)  # Session expires on browser close

            return redirect('patients_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html', {'request': request})

def register_view(request):     
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in and complete your profile.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration.html', {'form': form})

def generate_otp():
    """ Generate a 6-digit OTP """
    return random.randint(100000, 999999)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['user_id'] = user.id
            # Send OTP using Celery
            send_otp_email.delay(email, otp)
            request.session['otp_message'] = f'OTP sent to your email: {mask_email(email)}'
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, 'No user with this email')
    return render(request, 'forgot_password.html')


def verify_otp(request):    
    otp_message = request.session.pop('otp_message', None)
    if otp_message:
        messages.success(request, otp_message)

    if request.method == 'POST':
        try:
            user_otp = int(request.POST.get('otp'))
            session_otp = request.session.get('otp')

            if user_otp == session_otp:
                # Clear OTP from session after successful verification
                request.session.pop('otp', None)
                messages.success(request, 'OTP verified successfully!')
                return redirect('patients_reset_password')  # Redirect to reset password page
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid input. Please enter a valid OTP.')

    return render(request, 'verify_otp.html')

def reset_password(request):
    user_id = request.session.get('user_id')  # Get the user ID from session
    if not user_id:
        messages.error(request, 'Session expired or invalid. Please start over.')
        return redirect('forgot_password')

    user = User.objects.get(id=user_id)  # Get the user object

    if request.method == 'POST':
        form = ResetPasswordForm(user, request.POST)  # Pass the user object to the form
        if form.is_valid():
            form.save()
            logout(request)  # Log out the user after password reset
            messages.success(request, 'Password reset successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResetPasswordForm(user)  # Pass the user object to the form

    return render(request, 'patients_reset_password.html', {'form': form})


def mask_email(email):
    """ Mask the email to show only the first and last parts """
    try:
        local_part, domain = email.split('@')
        masked_local = local_part[0] + local_part[1] + local_part[2] + '***'  # Show first three letters only
        return f'{masked_local}@{domain}'
    except ValueError:
        return email

@login_required
def complete_profile(request):
    patient = request.user.patient
    user = request.user

    if not patient.must_complete_profile:
        return redirect('patients_dashboard')  # Already complete

    if request.method == 'POST':
        form = OnlinePatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            patient.must_complete_profile = False
            patient.save()
            return redirect('patients_dashboard')
    else:
        form = OnlinePatientForm(instance=patient, initial={
            'first_name': user.first_name,
            'last_name': user.last_name
        })

    return render(request, 'complete_profile.html', {'form': form})


@login_required
def patients_dashboard(request):
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, "Your profile is incomplete. Please contact support or register as a patient.")
        return redirect('home')

    # Check if profile is incomplete
    incomplete_profile = not all([
        patient.phone,
        patient.gender,
        patient.date_of_birth,
        patient.address,
        patient.city,
        patient.state,
        patient.zip_code
    ])

    return render(request, 'patients_dashboard.html', {
        'patient': patient,
        'incomplete_profile': incomplete_profile
    })

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def patient_billing(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    return render(request, 'patient_billing.html', {'appointments': appointments})

@login_required
def view_patient_profile(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'admins/patient_profile.html', {'patient': patient})

@login_required
def admin_edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    user_form = OfflinePatientUserForm(instance=patient.user)
    patient_form = OfflinePatientForm(instance=patient)

    if request.method == 'POST':
        user_form = OfflinePatientUserForm(request.POST, instance=patient.user)
        patient_form = OfflinePatientForm(request.POST, instance=patient)
        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            patient_form.save()
            messages.success(request, "Patient updated successfully.")
            return redirect('view_patients')

    return render(request, 'admins/edit_patient.html', {
        'user_form': user_form,
        'patient_form': patient_form,
        'patient': patient,
    })

@login_required
def staff_edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    user_form = OfflinePatientUserForm(instance=patient.user)
    patient_form = OfflinePatientForm(instance=patient)

    if request.method == 'POST':
        user_form = OfflinePatientUserForm(request.POST, instance=patient.user)
        patient_form = OfflinePatientForm(request.POST, instance=patient)
        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            patient_form.save()
            messages.success(request, "Patient updated successfully.")
            return redirect('staff_view_patients')

    return render(request, 'staff/staff_edit_patient.html', {
        'user_form': user_form,
        'patient_form': patient_form,
        'patient': patient,
    })

@login_required
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    user = patient.user
    if request.method == 'POST':
        patient.delete()
        user.delete()
        messages.success(request, "Patient deleted successfully.")
        return redirect('view_patients')
    return render(request, 'admins/delete_patient_confirm.html', {'patient': patient})

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

@login_required
def edit_patient_profile(request):
    patient = request.user.patient

    if request.method == 'POST':
        form = OnlinePatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patients_dashboard')
    else:
        form = OnlinePatientForm(
            instance=patient,
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        )

    return render(request, 'edit_profile.html', {'form': form})