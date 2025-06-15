from django.urls import path
from . import views

urlpatterns = [
    path('doctor_login/', views.doctor_login, name='doctor_login'),
    path('reset-password/', views.doctor_reset_password, name='doctor_reset_password'),
    path('logout/', views.doctor_logout, name='doctor_logout'),
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor_availability/', views.add_doctor_availability, name='doctor_availability'),
    path('patient/<int:id>/', views.view_patient_record, name='view_patient'),
    path('consult/<int:appointment_id>/', views.start_consultation, name='start_consultation'),
    path('consult/summary/<int:consultation_id>/', views.consultation_summary, name='consultation_summary'),
    path('consult/<int:consultation_id>/print-prescription/', views.print_prescription, name='print_prescription'),
    path('consult/<int:consultation_id>/print-lab/', views.print_lab_referral, name='print_lab_referral'),
    path('consult/<int:consultation_id>/print-xray/', views.print_xray_referral, name='print_xray_referral'),
]