from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    # path('cancel/', views.cancel_appointment, name='cancel_appointment'),
    # path('reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    # path('history/', views.appointment_history, name='appointment_history'),
    path('admin/appointments/', views.admin_appointments_list, name='admin_appointments_list'),
    path('admin/appointments/approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('admin/appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('staff/book/', views.staff_book_appointment, name='staff_book_appointment'),
    path('get-available-slots/', views.get_available_slots_api, name='get_available_slots'),
    path('get-available-dates/', views.get_available_dates, name='get_available_dates'),
    path('patients/book/', views.patients_book_appointment, name='patients_book_appointment'),
    path('api/recent/', views.recent_appointments_api, name='recent_appointments_api'),
    path('my-appointments/', views.my_appointments, name='my_appointments'), 
    path('patients/appointment/edit/<int:appointment_id>/', views.patient_edit_appointment, name='patient_edit_appointment'),
    path('patients/appointment/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('appointments/', views.staff_view_appointments, name='staff_view_appointments'),
    path('edit-appointment/<int:appointment_id>/', views.staff_edit_appointment, name='staff_edit_appointment'),
    path('delete-appointment/<int:appointment_id>/', views.staff_delete_appointment, name='staff_delete_appointment'),
]
