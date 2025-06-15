from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.patients_dashboard, name='patients_dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='patients_reset_password'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('patients/<int:patient_id>/', views.view_patient_profile, name='view_patient_profile'),
    path('patients/<int:patient_id>/edit/', views.admin_edit_patient, name='edit_patient'),
    path('staff-patients/<int:patient_id>/edit/', views.staff_edit_patient, name='staff_edit_patient'),
    path('patients/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    path('edit/', views.edit_patient_profile, name='edit_patient_profile'),
]