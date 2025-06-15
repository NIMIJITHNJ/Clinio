from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import StaffAppointmentForm
from .tasks import auto_approve_appointment
from django.http import JsonResponse
from doctors.models import DoctorAvailability
from .models import get_available_slots
from doctors.models import Doctor
from datetime import datetime, timedelta
from django.core import serializers
from django.shortcuts import get_object_or_404
from accounts.models import Bill
from appointments.forms import AppointmentForm, StaffEditAppointmentForm
from django.contrib.auth.decorators import user_passes_test
from admins.views import is_admin_or_staff
from django.urls import reverse_lazy
from decimal import Decimal 
from appointments.tasks import send_appointment_confirmation
from django.db import transaction



@login_required
def book_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')
        reason = request.POST.get('reason')
        doctor = User.objects.get(id=doctor_id)
        Appointment.objects.create(patient=request.user, doctor=doctor, date=date, time=time, reason=reason)
        return redirect('patients_home')
    
    doctors = User.objects.filter(is_staff=True)
    return render(request, 'appointments/book.html', {'doctors': doctors})

@login_required
def admin_appointments(request):
    appointments = Appointment.objects.all().order_by('-date')
    return render(request, 'appointments/admin_view.html', {'appointments': appointments})

@login_required
def admin_appointments_list(request):
    appointments = Appointment.objects.all().order_by('-date', '-time')
    return render(request, 'appointments/admin_list.html', {'appointments': appointments})

@login_required
def approve_appointment(request, appointment_id):
    appt = Appointment.objects.get(id=appointment_id)

    # Update appointment    
    appt.status = 'Approved'
    appt.set_fee_if_not_set()
    appt.save()

    # Send confirmation email via Celery
    if appt.patient.user.email:
        send_appointment_confirmation.delay(appt.id)

    # Create bill if it doesn't exist
    if not hasattr(appt, 'bill'):
        Bill.objects.create(
            appointment=appt,
            amount=appt.amount,
            notes='Consultation Fee'
        )

    messages.success(request, 'Appointment approved.')
    return redirect('admin_appointments_list')

@login_required
def cancel_appointment(request, appointment_id):
    appt = Appointment.objects.get(id=appointment_id)
    appt.status = 'Cancelled'
    appt.save()
    messages.success(request, 'Appointment cancelled.')
    return redirect('admin_appointments_list')

@login_required
def staff_book_appointment(request):
    form = StaffAppointmentForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            appointment = form.save(commit=False)
            raw_date = request.POST.get('date')
            raw_time = request.POST.get('time')

            try:
                selected_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
                selected_time = datetime.strptime(raw_time, '%H:%M').time()

                available_slots = get_available_slots(appointment.doctor, selected_date)
                if raw_time not in available_slots:
                    messages.error(request, "Selected time slot is no longer available.")
                    return redirect('staff_book_appointment')

                appointment.date = selected_date
                appointment.time = selected_time
                appointment.source = 'offline'
                appointment.save()
                transaction.on_commit(
                    lambda: auto_approve_appointment.apply_async(
                        args=[appointment.id],
                        countdown=30
                    )
                )
                messages.success(request, "Appointment booked successfully.")
                return redirect('staff_dashboard')

            except ValueError as e:
                messages.error(request, "Invalid date or time format.")
                print("Parsing error:", e)
                return redirect('staff_book_appointment')

        else:
            print("Form errors:", form.errors)

    return render(request, 'appointments/staff_book_appointment.html', {'form': form})

@login_required
def get_available_slots_api(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        availabilities = DoctorAvailability.objects.filter(doctor_id=doctor_id, date=date)

        if not availabilities.exists():
            return JsonResponse({'slots': []})

        slot_duration = timedelta(minutes=30)
        slots = []

        for availability in availabilities:
            start = datetime.combine(date, availability.start_time)
            end = datetime.combine(date, availability.end_time)

            while start + slot_duration <= end:
                slots.append(start.time().strftime("%H:%M"))
                start += slot_duration

        booked_times = Appointment.objects.filter(
            doctor__id=doctor_id,
            date=date
        ).values_list('time', flat=True)

        booked_strs = [bt.strftime("%H:%M") for bt in booked_times]
        available_slots = [slot for slot in slots if slot not in booked_strs]

        return JsonResponse({'slots': available_slots})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_available_dates(request):
    doctor_id = request.GET.get('doctor_id')

    try:
        # Doctor ID should match Doctor model's ID, not User ID
        doctor = Doctor.objects.get(id=doctor_id)
        print("Fetching dates for doctor_id:", doctor_id)
    except Doctor.DoesNotExist:
        return JsonResponse({'dates': []})

    # Get all distinct availability dates
    available_dates = DoctorAvailability.objects.filter(doctor=doctor).values_list('date', flat=True).distinct()
    formatted = [d.strftime('%Y-%m-%d') for d in available_dates]

    return JsonResponse({'dates': formatted})

@login_required
def patients_book_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')
        reason = request.POST.get('reason')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
            Appointment.objects.create(
                patient=request.user.patient,
                doctor=doctor,
                date=date,
                time=time,
                reason=reason,
                source='online',
            )
            messages.success(request, 'Appointment booked successfully.')
            return redirect('patients_dashboard')
        except Doctor.DoesNotExist:
            messages.error(request, 'Invalid doctor selection.')

    doctors = Doctor.objects.all()
    return render(request, 'appointments/patients_book_appointment.html', {'doctors': doctors})

@login_required
def recent_appointments_api(request):
    recent = Appointment.objects.order_by('-date')[:20]
    data = []
    for appt in recent:
        appt.refresh_from_db()  # <-- Ensures you get latest status
        data.append({
            'id': appt.id,
            'status': appt.status,
        })
    return JsonResponse({'appointments': data})

@login_required
def my_appointments(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')

    for appt in appointments:
        if appt.status == 'Approved' and appt.amount == 0:
            appt.set_fee_if_not_set()

    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})

@login_required
def patient_edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)
    doctors = Doctor.objects.all()


    if appointment.status != 'Pending':
        messages.error(request, "Only pending appointments can be edited.")
        return redirect('my_appointments')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated.")
            return redirect('my_appointments')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointments/edit_appointment.html', {'form': form, 'appointment': appointment, 'doctors': doctors})


@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)

    if appointment.status != 'Pending':
        messages.error(request, "Only pending appointments can be deleted.")
        return redirect('my_appointments')

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment deleted.")
        return redirect('my_appointments')

    return render(request, 'appointments/delete_appointment.html', {'appointment': appointment})

@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def staff_view_appointments(request):
    appointments = Appointment.objects.select_related('doctor__user', 'patient__user')

    for appt in appointments:
        if appt.status == 'Approved' and appt.amount == 0:
            appt.set_fee_if_not_set()

    return render(request, 'appointments/staff_view_appointments.html', {
        'appointments': appointments,
        'show_home_link': True,
        'show_logout': True,
    })

@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def staff_edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = StaffEditAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('staff_view_appointments')
    else:
        form = StaffEditAppointmentForm(instance=appointment)

    return render(request, 'appointments/staff_edit_appointment.html', {
        'form': form,
        'appointment': appointment       
    })

@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def staff_delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status == 'Approved' and appointment.payment_status == 'Unpaid':
        messages.error(request, "Cannot delete the appointment.")
        return redirect('staff_view_appointments')

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")
        return redirect('staff_view_appointments')

    return render(request, 'appointments/staff_delete_appointment.html', {'appointment': appointment})