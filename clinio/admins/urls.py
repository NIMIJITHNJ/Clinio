from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.admins_home, name='admins_home'),
    path('admins_login/', views.admins_login, name='admins_login'),
    path('admins_dashboard/', views.admins_dashboard, name='admins_dashboard'),
    path('admins_logout/', views.admins_logout, name='admins_logout'),
    path('appointment/<int:appointment_id>/status/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('ajax/update-status/', views.ajax_update_appointment_status, name='ajax_update_appointment_status'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),
    path('view-doctors/', views.view_doctors, name='view_doctors'),
    path('edit-doctor/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='admins/change_password.html',
        success_url='/admins/password-changed/'
    ), name='admin_change_password'),

    path('password-changed/', auth_views.PasswordChangeDoneView.as_view(
        template_name='admins/password_changed.html'
    ), name='admin_password_changed'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('view-staff/', views.view_staff, name='view_staff'),
    path('edit-staff/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('delete-doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('patients/', views.view_patients, name='view_patients'),
    path('appointments/', views.view_appointments, name='view_appointments'),
    path('edit-appointment/<int:appointment_id>/', views.admin_edit_appointment, name='admin_edit_appointment'),
    path('delete-appointment/<int:appointment_id>/', views.admin_delete_appointment, name='admin_delete_appointment'),
    path('admin/doctor-availability/', views.doctor_availability_report, name='doctor_availability_report'), 
       
    path('admin/offline-patient-registration/', views.admin_offline_patient_register, name='admin_offline_patient_register'),
]
