from django.shortcuts import render
from doctors.models import Doctor

def home(request):
    return render(request, 'home.html')
    

def about(request): 
    return render(request, 'about.html')

def book_appointment(request):
    return render(request, 'book_appointment.html')

def cardiology_view(request):
    return render(request, 'cardiology.html')

def general_medicine_view(request):
    return render(request, 'general_medicine.html')

def neurology_view(request):
    return render(request, 'neurology.html')

def orthopaedics_view(request):
    return render(request, 'orthopaedics.html')

def pediatrics_view(request):
    return render(request, 'pediatrics.html')

def dermatology_view(request):
    return render(request, 'dermatology.html')

def our_doctors_view(request):
    doctors = Doctor.objects.all()
    return render(request, 'our_doctors.html', {'doctors': doctors})

def contact_us_view(request):
    return render(request, 'contact_us.html')

def emergency_contact_view(request):
    return render(request, 'emergency_contact.html')