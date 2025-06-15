from celery import shared_task
from time import sleep
from .models import Appointment
from django.core.mail import send_mail
from django.db import connections, connection
from accounts.models import Bill

@shared_task
def auto_approve_appointment(appointment_id):       
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        if appointment.status == 'Pending':
            appointment.status = 'Approved'
            appointment.save()

            if not hasattr(appointment, 'bill'):
                Bill.objects.create(
                    appointment=appointment,
                    amount=appointment.amount,
                    notes='Consultation Fee'
                )
                
            #Send confirmation email
            if appointment.patient.user.email:
                send_appointment_confirmation.delay(appointment.id)
    except Appointment.DoesNotExist:
        pass

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_appointment_confirmation(self, appointment_id):
    print(f"[CELERY] Running send_appointment_confirmation for ID: {appointment_id}")
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        email = appointment.patient.user.email
        if email:
            send_mail(
                subject='Appointment Confirmed – CareWell',
                message=f"Dear {appointment.patient.user.first_name},\n\nYour appointment with Dr. {appointment.doctor.name} on {appointment.date} at {appointment.time} has been confirmed.\n\nThank you,\nCareWell",
                from_email='carewellmsh@gmail.com',
                recipient_list=[email],
                fail_silently=False
            )
            print("[CELERY] Email sent successfully.")
        else:
            print(f"[CELERY] No email found for patient ID {appointment.patient.id}")
    except Appointment.DoesNotExist as e:
        print(f"[CELERY ERROR] {e}")
        connections['default'].ensure_connection()
        connection.close() 
        raise self.retry(exc=e)

