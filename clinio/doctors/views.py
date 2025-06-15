from django.shortcuts import render, redirect, get_object_or_404
from .forms import DoctorAvailabilityForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import get_messages
from appointments.models import Appointment
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from doctors.models import Doctor
from patients.models import Patient
from .forms import ConsultationForm 
from appointments.models import Consultation
from patients.views import calculate_age
from .pdf_utils import render_to_pdf
from django.http import HttpResponse
from django.utils.timezone import now
from .models import Prescription, LabReferral, XRayReferral
from django.http import HttpResponseForbidden
from doctors.utils.generate_prescription_pdf import generate_prescription_pdf
from django.http import FileResponse
from doctors.utils.generate_referral_pdf import generate_referral_pdf

def doctors_home(request):
    return render(request, 'doctors_home.html')

@login_required
def add_doctor_availability(request):
    if request.method == 'POST':
        form = DoctorAvailabilityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor availability added.")
            return redirect('doctor_availability')
    else:
        form = DoctorAvailabilityForm()
    return render(request, 'doctors/add_availability.html', {'form': form})

from datetime import date, timedelta
from django.utils.timezone import now

@login_required
def doctor_dashboard(request):
    doctor = request.user.doctor

    # All approved upcoming appointments
    appointments = Appointment.objects.filter(
        doctor=doctor,
        status='Approved',
        date__gte=date.today()
    ).order_by('date', 'time')

    # Appointments today
    appointments_today = appointments.filter(date=date.today()).count()

    # This week's appointments
    week_start = date.today()
    week_end = week_start + timedelta(days=6)
    weekly_appointments = appointments.filter(date__range=(week_start, week_end)).count()

    # Get future slots (today onwards), approved, without consultation
    next_appt = Appointment.objects.filter(
        doctor=request.user.doctor,
        date__gte=now().date(),
        status='Approved'
    ).exclude(consultation__isnull=False).order_by('date', 'time').first()

    next_slot = next_appt.time.strftime("%I:%M %p").lstrip("0") if next_appt else None

    # Assigned patients (unique patients from appointments)
    patient_ids = appointments.values_list('patient_id', flat=True).distinct()
    assigned_patients = Patient.objects.filter(id__in=patient_ids)
    for patient in assigned_patients:
        patient.age = calculate_age(patient.date_of_birth) if patient.date_of_birth else None

    return render(request, 'doctors/doctor_dashboard.html', {
        'appointments': appointments,
        'appointments_today': appointments_today,
        'weekly_appointments': weekly_appointments,
        'next_slot': next_slot,
        'total_patients': assigned_patients.count(),
        'assigned_patients': assigned_patients,
        'doctor': doctor,        
        'show_logout': True,
        'show_home_link': True,
        'next_slot': next_slot,
    })


def doctor_login(request):
    if request.method == 'GET' and not request.GET.get('from_logout'):
        list(get_messages(request))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'doctor'):
            login(request, user)
            doctor = Doctor.objects.get(user=user)
            if doctor.must_reset_password:
                return redirect('doctor_reset_password')
            messages.success(request, f"Welcome, Dr. {doctor.name}!")
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a doctor account.')
    return render(request, 'doctors/doctor_login.html')

@login_required
def doctor_reset_password(request):
    doctor = Doctor.objects.get(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            doctor.must_reset_password = False
            doctor.save()
            messages.success(request, 'Password updated. Please log in again.')
            return redirect('doctor_login')
        else:
            messages.error(request, 'Password reset failed. Please fix the errors.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'doctors/doctor_reset_password.html', {
        'form': form,
        'show_logout': False,
        'show_home_link': False
    })

@login_required
def doctor_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('doctor_login')

@login_required
def view_patient_record(request, id):
    patient = get_object_or_404(Patient, id=id)
    age = calculate_age(patient.date_of_birth) if patient.date_of_birth else None
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date')
    lab_reports = LabReferral.objects.filter(patient=patient).order_by('-date')
    xray_reports = XRayReferral.objects.filter(patient=patient).order_by('-date')

    context = {
        'patient': patient,
        'age': age,
        'prescriptions': prescriptions,
        'lab_reports': lab_reports,
        'xray_reports': xray_reports,
    }

    if hasattr(request.user, 'doctor'):
        return render(request, 'doctors/view_patient_record.html', context)
    elif hasattr(request.user, 'staff'):
        return render(request, 'staff/view_patient_record.html', context)
    elif request.user.is_superuser:
        return render(request, 'admins/view_patient_record.html', context)
    else:
        return HttpResponseForbidden("You are not allowed to view this record.")

@login_required
def start_consultation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)

    # Prevent duplicate form
    if hasattr(appointment, 'consultation'):
        messages.info(request, "Consultation already recorded.")
        return redirect('doctor_dashboard')

    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.appointment = appointment
            consultation.save()

            Prescription.objects.create(
                patient=appointment.patient,
                doctor=appointment.doctor,
                consultation=consultation,
                details=consultation.prescription
            )

            messages.success(request, "Consultation saved successfully.")
            return redirect('consultation_summary', consultation_id=consultation.id)
    else:
        form = ConsultationForm()

    return render(request, 'doctors/start_consultation.html', {
        'form': form,
        'appointment': appointment,
        'patient': appointment.patient,
    })

@login_required
def consultation_summary(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    appointment = consultation.appointment
    patient = appointment.patient

    return render(request, 'doctors/consultation_summary.html', {
        'consultation': consultation,
        'appointment': appointment,
        'patient': patient,
        'show_logout': True,
        'show_home_link': True,
    })

@login_required
def print_prescription(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    appointment = consultation.appointment
    patient = appointment.patient

    pdf_buffer = generate_prescription_pdf(consultation)
    filename = f"Prescription_{consultation.appointment.patient.user.get_full_name()}.pdf"

    return FileResponse(pdf_buffer, as_attachment=False, filename=filename, content_type='application/pdf')

@login_required
def print_lab_referral(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    pdf = generate_referral_pdf(consultation, type="lab")
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Lab_Referral_{consultation.appointment.patient.user.get_full_name()}.pdf"'
    return response

@login_required
def print_xray_referral(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    pdf = generate_referral_pdf(consultation, type="xray")
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="XRay_Referral_{consultation.appointment.patient.user.get_full_name()}.pdf"'
    return response

