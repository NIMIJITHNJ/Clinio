from django.contrib.auth.models import User
from django.db import models

class StaffRole(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField("Full Name", max_length=100)
    phone = models.CharField("Phone Number", max_length=20, blank=True)
    roles = models.ManyToManyField(StaffRole)  
    profile_pic = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    must_reset_password = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
