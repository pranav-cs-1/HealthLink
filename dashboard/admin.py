from django.contrib import admin
from .models import Patient, MedicalProfessional, HealthcareFacilityAdministrator, Appointment, TestResult

admin.site.register(Patient)
admin.site.register(MedicalProfessional)
admin.site.register(HealthcareFacilityAdministrator)
admin.site.register(Appointment)
admin.site.register(TestResult)
