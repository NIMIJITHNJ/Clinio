from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),      
    path('specialities/cardiology/', views.cardiology_view, name='cardiology'),
    path('specialities/general-medicine/', views.general_medicine_view, name='general_medicine'),
    path('specialities/neurology/', views.neurology_view, name='neurology'),
    path('specialities/orthopaedics/', views.orthopaedics_view, name='orthopaedics'),
    path('specialities/pediatrics/', views.pediatrics_view, name='pediatrics'),
    path('specialities/dermatology/', views.dermatology_view, name='dermatology'),
    path('our-doctors/', views.our_doctors_view, name='our_doctors'),
    path('contact-us/', views.contact_us_view, name='contact_us'),
    path('emergency/', views.emergency_contact_view, name='emergency_contact'),
]