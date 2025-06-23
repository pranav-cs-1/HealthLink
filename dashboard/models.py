from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    # Add these new fields to connect reports with patients and doctors
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='reports', null=True)
    medical_professional = models.ForeignKey('MedicalProfessional', on_delete=models.CASCADE,
                                             related_name='authored_reports', null=True)

    def __str__(self):
        return self.title

class MedicalProfessionalPatient(models.Model):
    medical_professional = models.ForeignKey('MedicalProfessional', on_delete=models.CASCADE)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)

    class Meta:
        # Ensure that a given pairing of medical professional and patient is unique.
        unique_together = ('medical_professional', 'patient')
        # Optionally set a custom table name
        db_table = 'dashboard_medicalprofessional_patients'

    def __str__(self):
        return f"{self.medical_professional} - {self.patient}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} (Patient)"

class MedicalProfessional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    # Explicit many-to-many relationship using the through model
    patients = models.ManyToManyField('Patient', blank=True,
                                      related_name='assigned_doctors',
                                      through='MedicalProfessionalPatient')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} (Doctor)"

class HealthcareFacilityAdministrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facility_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} (Admin of {self.facility_name})"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medical_professional = models.ForeignKey(MedicalProfessional, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    reason = models.TextField()

    def __str__(self):
        return f"Appointment on {self.appointment_date} for {self.patient}"

class TestResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medical_professional = models.ForeignKey(MedicalProfessional, on_delete=models.SET_NULL, null=True)
    test_date = models.DateTimeField()
    description = models.TextField()
    result_data = models.TextField()

    def __str__(self):
        return f"TestResult for {self.patient} on {self.test_date}"

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medical_professional = models.ForeignKey(MedicalProfessional, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient} - {self.medication_name}"
