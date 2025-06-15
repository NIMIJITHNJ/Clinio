from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Staff
from patients.forms import OfflinePatientForm
from patients.forms import OfflinePatientUserForm
from patients.models import Patient
from django.contrib.auth.models import User
from django.contrib.auth import logout
from appointments.models import Appointment
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from admins.views import is_admin_or_staff
from django.urls import reverse_lazy    
from django.contrib.auth.decorators import user_passes_test
from doctors.forms import LabReferralForm, XRayReferralForm

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            staff = Staff.objects.get(user=user)
            if staff.must_reset_password:
                return redirect('reset_password')
            name = user.first_name or user.username
            messages.success(request, f"Welcome, {name}!")
            return redirect('staff_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a staff account.')
    return render(request, 'staff/staff_login.html')

@login_required
def reset_password(request):
    staff = Staff.objects.get(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            staff.must_reset_password = False
            staff.save()
            messages.success(request, 'Password updated successfully. Please log in again with your new password.')
            return redirect('staff_login')
        else:
            messages.error(request, 'Password reset failed. Please fix the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'staff/reset_password.html', {
        'form': form,
        'show_logout': False,
        'show_home_link': False
    })

@login_required
def staff_dashboard(request):
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='Pending').count()
    appointments_today = Appointment.objects.filter(date=now().date()).count()
    recent_appointments = Appointment.objects.order_by('-id')
    paginator = Paginator(recent_appointments, 10)  # 10 per page
    page_number = request.GET.get("page")
    recent_appointments = paginator.get_page(page_number)    

    return render(request, 'staff/staff_dashboard.html', {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'appointments_today': appointments_today,
        'recent_appointments': recent_appointments,
        'staff_name': request.user.first_name or request.user.username,
        'show_logout': True,
        'show_home_link': True
    })

@login_required
def offline_patient_register(request):
    if request.method == 'POST':
        user_form = OfflinePatientUserForm(request.POST)
        patient_form = OfflinePatientForm(request.POST)

        if user_form.is_valid() and patient_form.is_valid():
            user = user_form.save(commit=False)

            # Create unique username using name or fallback
            base_username = (user.first_name + user.last_name).lower() or "patient"
            counter = 1
            while User.objects.filter(username=base_username + str(counter)).exists():
                counter += 1
            user.username = base_username + str(counter)

            temp_password = get_random_string(length=10)
            user.set_password(temp_password)
            user.save()

            patient = patient_form.save(commit=False)
            patient.user = user
            patient.registered_by = 'staff'
            patient.save()

            messages.success(request, 'Offline patient registered successfully.')
            return redirect('staff_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = OfflinePatientUserForm()
        patient_form = OfflinePatientForm()

    return render(request, 'staff/offline_patient_register.html', {
        'form': {
            'user_form': user_form,
            'patient_form': patient_form
        },
        'show_logout': True,
        'show_home_link': True
    })

@login_required
def staff_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('staff_login')

@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def staff_view_patients(request):
    patients = Patient.objects.all().select_related('user')
    return render(request, 'staff/staff_view_patients.html', {
        'patients': patients,
        'show_home_link': True,
        'show_logout': True,
    })

@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def upload_lab_report(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = LabReferralForm(request.POST, request.FILES)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.patient = patient
            lab.save()
            messages.success(request, "Lab report uploaded successfully.")
            return redirect('view_patient', id=patient.id)
    else:
        form = LabReferralForm()

    return render(request, 'staff/upload_report.html', {
        'form': form,
        'patient': patient,
        'report_type': "Lab Report"
    })



@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def upload_xray_report(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = XRayReferralForm(request.POST, request.FILES)
        if form.is_valid():
            xray = form.save(commit=False)
            xray.patient = patient
            xray.save()
            messages.success(request, "X-Ray report uploaded successfully.")
            return redirect('view_patient', id=patient.id)
    else:
        form = XRayReferralForm()

    return render(request, 'staff/upload_report.html', {
        'form': form,
        'patient': patient,
        'report_type': "Scan Report"
    })
