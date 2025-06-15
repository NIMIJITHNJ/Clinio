from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import date
from patients.models import Patient
from doctors.models import Doctor
from staff.models import Staff
from appointments.models import Appointment
from django.db.models import Count
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.models import User
import random, string
from doctors.forms import DoctorUserForm, DoctorForm
from staff.forms import StaffForm, StaffUserForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from datetime import timedelta, date
from collections import defaultdict
from doctors.models import DoctorAvailability
import json
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from appointments.forms import AppointmentForm, AdminAppointmentForm 
from appointments.tasks import send_appointment_confirmation
from accounts.models import Bill
from patients.forms import OfflinePatientForm, OfflinePatientUserForm
from django.utils.crypto import get_random_string
from django.db import transaction

def admins_home(request):
    return render(request, 'admins_home.html')

def admins_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            messages.success(request, 'Welcome, Admin!')
            return redirect('admins_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin user.')
    return render(request, 'admins_login.html')

@login_required
def admins_dashboard(request):
    # Fetch filter params
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    doctor_filter = request.GET.get('doctor')

    # Base queryset
    recent_appointments = Appointment.objects.all()

    # Apply filters
    if status_filter:
        recent_appointments = recent_appointments.filter(status=status_filter)
    if date_filter:
        parsed_date = parse_date(date_filter)
        if parsed_date:
            recent_appointments = recent_appointments.filter(date=parsed_date)
    if doctor_filter:
        recent_appointments = recent_appointments.filter(doctor_id=doctor_filter)

    # Sorting and limiting results
    recent_appointments = recent_appointments.order_by('-date', '-time')
    paginator = Paginator(recent_appointments, 10)  # 10 per page
    page_number = request.GET.get("page")
    recent_appointments = paginator.get_page(page_number)

    
    
    # Dashboard stats
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_staff = Staff.objects.count()  
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='Pending').count()
    appointments_today = Appointment.objects.filter(date=date.today()).count() 
    start_date = date.today() - timedelta(days=6)   

    # Appointments trend for pie chart
    appointments_by_day = (
        Appointment.objects
        .filter(date__gte=start_date)
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Doctor-wise appointment count per day for bar chart
    appointments_qs = (
        Appointment.objects
        .filter(date__gte=start_date)
        .values('doctor__user__first_name', 'date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    doctor_availability_by_date = defaultdict(lambda: defaultdict(int))
    for entry in appointments_qs:
        doctor_availability_by_date[entry['date']][entry['doctor__user__first_name']] = entry['count']

    availability_labels = sorted(doctor_availability_by_date.keys())
    doctor_names = sorted({doc for d in availability_labels for doc in doctor_availability_by_date[d]})

    colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f']
    availability_datasets = []
    for i, doctor in enumerate(doctor_names):
        data = [doctor_availability_by_date[d].get(doctor, 0) for d in availability_labels]
        availability_datasets.append({
            'label': doctor,
            'data': data,
            'backgroundColor': colors[i % len(colors)]
        })

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_staff': total_staff,  
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'appointments_today': appointments_today,
        'appointments_by_day': list(appointments_by_day),
        'recent_appointments': recent_appointments,
        'doctors': Doctor.objects.all(),  
        'availability_labels': json.dumps([str(d) for d in availability_labels]),
        'availability_datasets': json.dumps(availability_datasets),
    }
    return render(request, 'admins/dashboard.html', context)


def admins_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('admins_login')

@login_required
def update_appointment_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if status in ['Approved', 'Cancelled']:
        appointment.status = status
        appointment.save()
        messages.success(request, f"Appointment #{appointment_id} marked as {status}.")
    else:
        messages.error(request, "Invalid status.")
    return redirect('admins_dashboard')

@csrf_exempt
@require_POST
@login_required
def ajax_update_appointment_status(request):
    from appointments.models import Appointment
    import json

    try:
        data = json.loads(request.body)
        appointment_id = data.get('id')
        new_status = data.get('status')

        appt = Appointment.objects.get(id=appointment_id)
        if new_status in ['Approved', 'Cancelled']:
            appt.status = new_status
            appt.save()

            # CELERY TRIGGER
            if new_status == 'Approved' and appt.patient.user.email:
                transaction.on_commit(lambda: send_appointment_confirmation.apply_async((appt.id,), countdown=3))

                # BILL CREATION
                if not hasattr(appt, 'bill'):
                    Bill.objects.create(
                        appointment=appt,
                        amount=appt.amount,
                        notes='Consultation Fee'
                    )
    
            return JsonResponse({'success': True, 'status': new_status})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def generate_temp_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@login_required
def add_doctor(request):
    if request.method == 'POST':
        user_form = DoctorUserForm(request.POST)
        doctor_form = DoctorForm(request.POST, request.FILES)
        if user_form.is_valid() and doctor_form.is_valid():
            temp_password = generate_temp_password()
            user = user_form.save(commit=False)
            user.set_password(temp_password)
            user.save()

            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.name = f"{user.first_name} {user.last_name}"
            doctor.save()

            send_mail(
                subject='Your Doctor Account for CareWell',
                message=f'Hi Dr. {user.first_name},\n\nUser ID: {user.username}\nTemp Password: {temp_password}',
                from_email='carewellmsh@gmail.com',
                recipient_list=[user.email],
                fail_silently=False
            )
            return redirect('admins_dashboard')
    else:
        user_form = DoctorUserForm()
        doctor_form = DoctorForm()
    
    return render(request, 'admins/add_doctor.html', {
        'user_form': user_form,
        'doctor_form': doctor_form
    })
@login_required
def view_doctors(request):
    doctors = Doctor.objects.all()
    return render(request, 'admins/view_doctors.html', {'doctors': doctors})

@login_required
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    user = doctor.user

    if request.method == 'POST':
        user_form = DoctorUserForm(request.POST, instance=user)
        doctor_form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if user_form.is_valid() and doctor_form.is_valid():
            user_form.save()
            doctor_form.save()
            return redirect('view_doctors')
    else:
        user_form = DoctorUserForm(instance=user)
        doctor_form = DoctorForm(instance=doctor)

    return render(request, 'admins/edit_doctor.html', {
        'user_form': user_form,
        'doctor_form': doctor_form,
        'doctor': doctor
    })

@login_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    user = doctor.user
    if request.method == 'POST':
        user.delete()  
        messages.success(request, 'Doctor deleted successfully.')
        return redirect('view_doctors')
    return render(request, 'admins/delete_doctor_confirm.html', {'doctor': doctor})

@login_required
def add_staff(request):
    if request.method == 'POST':
        user_form = StaffUserForm(request.POST)
        staff_form = StaffForm(request.POST, request.FILES)
        if user_form.is_valid() and staff_form.is_valid():
            temp_password = generate_temp_password()
            user = user_form.save(commit=False)
            user.set_password(temp_password)
            user.is_staff = True # Ensure the user is marked as staff   
            user.save()

            staff = staff_form.save(commit=False)
            staff.user = user
            staff.name = f"{user.first_name} {user.last_name}"
            staff.must_reset_password = True
            staff.save()
            staff_form.save_m2m() 

            send_mail(
                subject='Your Staff Account for CareWell',
                message=f'Hi {user.first_name},\n\nUser ID: {user.username}\nTemp Password: {temp_password}',
                from_email='carewellmsh@gmail.com',
                recipient_list=[user.email],
                fail_silently=False
            )
            return redirect('admins_dashboard')
    else:
        user_form = StaffUserForm()
        staff_form = StaffForm()

    return render(request, 'admins/add_staff.html', {
        'user_form': user_form,
        'staff_form': staff_form
    })

@login_required
def view_staff(request):
    staff_members = Staff.objects.all()
    return render(request, 'admins/view_staff.html', {'staff_members': staff_members})

@login_required
def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    user = staff.user

    if request.method == 'POST':
        user_form = StaffUserForm(request.POST, instance=user)
        staff_form = StaffForm(request.POST, request.FILES, instance=staff)
        if user_form.is_valid() and staff_form.is_valid():
            user_form.save()
            staff_form.save()
            return redirect('view_staff')
    else:
        user_form = StaffUserForm(instance=user)
        staff_form = StaffForm(instance=staff)

    return render(request, 'admins/edit_staff.html', {
        'user_form': user_form,
        'staff_form': staff_form,
        'staff': staff
    })

@login_required
def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    user = staff.user
    if request.method == 'POST':
        user.delete()  # this will also delete the staff due to OneToOne relation
        messages.success(request, 'Staff member deleted successfully.')
        return redirect('view_staff')
    return render(request, 'admins/delete_staff_confirm.html', {'staff': staff})

def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def view_patients(request):
    patients = Patient.objects.all().select_related('user')
    return render(request, 'admins/view_patients.html', {'patients': patients})


@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def view_appointments(request):
    appointments = Appointment.objects.select_related('doctor__user', 'patient__user')

    for appt in appointments:
        if appt.status == 'Approved' and appt.amount == 0:
            appt.set_fee_if_not_set()

    return render(request, 'admins/view_appointments.html', {'appointments': appointments})

@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def admin_edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AdminAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('view_appointments')
    else:
        form = AdminAppointmentForm(instance=appointment)

    return render(request, 'admins/edit_appointment.html', {
        'form': form,
        'appointment': appointment       
    })

@user_passes_test(is_admin_or_staff, login_url=reverse_lazy('admins_login'))
def admin_delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.payment_status == 'paid':
        messages.error(request, "Cannot delete a paid appointment.")
        return redirect('view_appointments')

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")
        return redirect('view_appointments')

    return render(request, 'admins/delete_appointment.html', {'appointment': appointment})

def doctor_availability_report(request):
    doctor_id = request.GET.get('doctor')
    selected_date = request.GET.get('date')
    availabilities = DoctorAvailability.objects.all()

    if doctor_id:
        availabilities = availabilities.filter(doctor__id=doctor_id)
    if selected_date:
        availabilities = availabilities.filter(date=selected_date)

    # Gather booked slots
    booked_slots = {}
    for slot in availabilities:
        booked = Appointment.objects.filter(
            doctor=slot.doctor,
            date=slot.date,
            status='Approved'
        ).values_list('time', flat=True)
        booked_slots[slot.id] = sorted(booked) 

    return render(request, 'admins/doctor_availability_report.html', {
        'availabilities': availabilities,
        'doctors': Doctor.objects.all(),
        'selected_doctor': doctor_id,
        'selected_date': selected_date,
        'booked_slots': booked_slots
    })

@login_required
def admin_offline_patient_register(request):
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
            patient.registered_by = 'admin'
            patient.save()

            messages.success(request, 'Patient added successfully.')
            return redirect('admins_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = OfflinePatientUserForm()
        patient_form = OfflinePatientForm()

    return render(request, 'admins/admin_offline_patient_register.html', {
        'form': {
            'user_form': user_form,
            'patient_form': patient_form
        },
        'show_logout': True,
        'show_home_link': True
    })