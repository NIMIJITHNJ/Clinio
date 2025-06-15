from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Patient

@receiver(user_signed_up)
def create_patient_profile_on_google_signup(request, user, **kwargs):
    if not hasattr(user, 'patient'):
        Patient.objects.create(user=user, registered_by='google')
