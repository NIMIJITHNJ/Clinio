from celery import shared_task
from django.core.mail import send_mail
import random

@shared_task
def send_otp_email(email, otp):
    subject = 'Your OTP for Password Reset'
    message = f'Your OTP for resetting your password is: {otp}'
    from_email = 'carewellmsh@gmail.com'
    send_mail(subject, message, from_email, [email])
    return "OTP sent successfully"
