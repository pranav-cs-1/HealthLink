# hospital_management/urls.py
from django.contrib import admin
from django.urls import path, include
from dashboard import views

urlpatterns = [
    path('admin/patients/', views.admin_patients, name='admin_patients'),
    path('admin/doctors/', views.admin_doctors, name='admin_doctors'),
    path('admin/appointments/', views.admin_appointments, name='admin_appointments'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/new_patient/', views.admin_new_patient, name='admin_new_patient'),
    path('admin/new_doctor/', views.admin_new_doctor, name='admin_new_doctor'),
    path('admin/new_appointment/', views.admin_new_appointment, name='admin_new_appointment'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    path('login/', views.user_login, name='login'),

    # Separate logins for each role
    path('login/patient/', views.patient_login, name='patient_login'),
    path('login/medical/', views.medical_login, name='medical_login'),
    path('login/admin/', views.admin_login, name='admin_login'),

    # Dashboard
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),

    path('dashboard/patient/billing', views.patient_billing, name='patient_billing'),
    path('dashboard/medical/', views.medical_dashboard, name='medical_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/medical/new_appointment/', views.medical_new_appointment, name='medical_new_appointment'),
    path('dashboard/medical/new_prescription/', views.medical_new_prescription, name='medical_new_prescription'),
    path('dashboard/api/generate-description/', views.generate_drug_description, name='generate_drug_description'),
    path('dashboard/medical/new_patient/', views.medical_new_patient, name='medical_new_patient'),
    path('dashboard/medical/patients/', views.medical_patients, name='medical_patients'),
    path('dashboard/medical/patient/<int:patient_id>/', views.medical_patient_detail, name='medical_patient_detail'),
    path('dashboard/patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('dashboard/patient/appointments/<int:appointment_id>/edit/', views.patient_edit_appointment, name='patient_edit_appointment'),
    path('dashboard/patient/appointments/<int:appointment_id>/delete/', views.patient_delete_appointment, name='patient_delete_appointment'),
    path('dashboard/patient/prescriptions/', views.patient_prescriptions, name='patient_prescriptions'),
    path('dashboard/patient/find_pharmacy/', views.find_pharmacy, name='find_pharmacy'),
    path('dashboard/medical/new_patient/', views.medical_new_patient, name='medical_new_patient'),

    path('signup/patient/', views.patient_signup, name='patient_signup'),
    path('signup/medical/', views.medical_signup, name='medical_signup'),
    path('signup/admin/', views.admin_signup, name='admin_signup'),

    path('dashboard/patient/new_appointment/', views.patient_new_appointment, name='patient_new_appointment'),

    path('dashboard/medical/new_report/', views.medical_new_report, name='medical_new_report'),
    path('dashboard/patient/reports/', views.patient_view_reports, name='patient_view_reports'),
    path('dashboard/medical/reports/', views.medical_view_reports, name='medical_view_reports'),
    path('dashboard/report/<int:report_id>/', views.report_detail, name='report_detail'),

    path('facility-admin/patients/<int:patient_id>/view/', views.admin_view_patient, name='admin_view_patient'),
    path('facility-admin/patients/<int:patient_id>/edit/', views.admin_edit_patient, name='admin_edit_patient'),
    path('facility-admin/patients/<int:patient_id>/delete/', views.admin_delete_patient, name='admin_delete_patient'),
    path('facility-admin/doctors/<int:doctor_id>/view/', views.admin_view_doctor, name='admin_view_doctor'),
    path('facility-admin/doctors/<int:doctor_id>/edit/', views.admin_edit_doctor, name='admin_edit_doctor'),
    path('facility-admin/doctors/<int:doctor_id>/delete/', views.admin_delete_doctor, name='admin_delete_doctor'),
    path('facility-admin/appointments/<int:appointment_id>/edit/',
         views.admin_edit_appointment,
         name='admin_edit_appointment'),
    path('facility-admin/appointments/<int:appointment_id>/delete/',
         views.admin_delete_appointment,
         name='admin_delete_appointment'),
]
