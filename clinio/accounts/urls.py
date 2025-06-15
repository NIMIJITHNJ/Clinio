from . import views
from django.urls import path


urlpatterns = [
    path('billing/', views.billing_dashboard, name='billing_dashboard'),
    path('billing/generate/<int:appointment_id>/', views.generate_invoice_pdf, name='generate_invoice'),
    path('dummy-payment/<int:appointment_id>/', views.payment_page, name='payment_page'),
    path('billing/', views.billing_dashboard, name='billing_dashboard'),
    path('billing/mark-paid/<int:appointment_id>/', views.mark_payment, name='staff_mark_payment'),
    path('invoice/<int:appointment_id>/', views.generate_invoice_view, name='print_invoice'),
    path('admin/amount-report/', views.amount_collected_report, name='amount_collected_report'),
]