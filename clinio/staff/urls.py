from django.urls import path
from . import views


urlpatterns = [    
    path('staff_login/', views.staff_login, name='staff_login'),
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('offline_patient_register/', views.offline_patient_register, name='offline_patient_register'),
    path('staff_logout/', views.staff_logout, name='staff_logout'),
    path('staff-view-patients/', views.staff_view_patients, name='staff_view_patients'),
    path('upload/lab/<int:patient_id>/', views.upload_lab_report, name='upload_lab_report'),
    path('upload/xray/<int:patient_id>/', views.upload_xray_report, name='upload_xray_report'),
]