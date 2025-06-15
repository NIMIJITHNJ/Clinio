from django.shortcuts import render, get_object_or_404, redirect
from appointments.models import Appointment
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from .utils import generate_invoice_pdf
from django.http import FileResponse, Http404, JsonResponse
from django.urls import reverse
from django.db.models import Sum, Q
from django.utils.dateparse import parse_date

@login_required
def billing_dashboard(request):
    unpaid_appointments = Appointment.objects.filter(
        status='Approved',
        payment_status='unpaid',
        amount__gt=0
    ).order_by('-date')

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')

        appointment = get_object_or_404(Appointment, id=appointment_id)

        appointment.payment_status = 'paid'
        appointment.payment_method = payment_method
        if transaction_id:
            appointment.transaction_id = transaction_id
        appointment.save()

        messages.success(request, f"Payment recorded for appointment #{appointment.id}.")        

    return render(request, 'accounts/billing_dashboard.html', {
        'unpaid_appointments': unpaid_appointments,
        'show_logout': True,
        'show_home_link': True
    })

@login_required
def payment_page(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)

    if appointment.status != 'Approved':
        messages.error(request, "Only approved appointments can be paid.")
        return redirect('my_appointments')

    appointment.set_fee_if_not_set()

    if request.method == 'POST':
        # Determine which form was active based on available input
        upi_id = request.POST.get('upi_id')
        card_number = request.POST.get('card_number')

        if upi_id:
            method = 'upi'
        elif card_number:
            method = 'card'
        else:
            messages.error(request, "Please complete the payment details.")
            return redirect('payment_page', appointment_id=appointment_id)        


        appointment.payment_status = 'paid'
        appointment.payment_method = method
        if not appointment.invoice_number:
            appointment.invoice_number = f"INV{appointment.id:05d}"  
        appointment.save()

        # Generate PDF
        pdf_file = generate_invoice_pdf(appointment)

        # Prepare and send email
        email = EmailMessage(
            subject='Appointment Payment Confirmation - CareWell Hospital',
            body='Thank you for your payment. Please find attached the invoice for your appointment.',
            to=[appointment.patient.user.email]
        )
        email.attach('invoice.pdf', pdf_file.read(), 'application/pdf')
        email.send()

        messages.success(request, "Payment successful. A confirmation email has been sent.")
        return render(request, 'accounts/payment_success.html', {'redirect_url': 'my_appointments'})

    return render(request, 'accounts/payment_page.html', {
        'appointment': appointment,
        'appointment_fee': appointment.amount
    })

@login_required
def mark_payment(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.payment_status == 'paid':
            messages.info(request, "This appointment is already marked as paid.")
            return redirect('print_invoice', appointment_id=appointment.id)

        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')

        appointment.payment_status = 'paid'
        appointment.payment_method = payment_method
        if transaction_id:
            appointment.transaction_id = transaction_id        
        if not appointment.invoice_number:
            appointment.invoice_number = f"INV{appointment.id:05d}"  
        appointment.save()

        messages.success(request, f"Payment recorded for appointment #{appointment.id}.")
        return JsonResponse({'redirect_url': reverse('print_invoice', args=[appointment.id])})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def generate_invoice_view(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        raise Http404("Appointment not found.")

    if appointment.payment_status != 'paid':
        messages.error(request, "Invoice available only for paid appointments.")
        return redirect('admin_appointments_list')  # or staff_billing

    pdf_file = generate_invoice_pdf(appointment)
    return FileResponse(pdf_file, as_attachment=False, filename='invoice.pdf') 

@login_required
def amount_collected_report(request):
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    filters = Q(status='Approved') & Q(payment_status='paid')

    if date_from:
        filters &= Q(date__gte=parse_date(date_from))
    if date_to:
        filters &= Q(date__lte=parse_date(date_to))

    total_amount = Appointment.objects.filter(filters).aggregate(Sum('amount'))['amount__sum'] or 0
    appointments = Appointment.objects.filter(filters)

    return render(request, 'admins/collection_report.html', {
        'appointments': appointments,
        'total_amount': total_amount,
        'date_from': date_from,
        'date_to': date_to,
    })