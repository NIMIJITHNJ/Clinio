from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='other')
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    registered_by = models.CharField(
        max_length=10,
        choices=[('online', 'Online'), ('staff', 'Staff')],
        default='online'
    )
    must_complete_profile = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"