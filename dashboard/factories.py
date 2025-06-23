# dashboard/factories.py
from .models import Report, Appointment, Patient, MedicalProfessional, HealthcareFacilityAdministrator
from django.contrib.auth.models import User

class BaseFactory:
    def create(self, **kwargs):
        raise NotImplementedError("Must implement create()")

class UserProfileFactory(BaseFactory):
    """
    A factory that creates the right profile (Patient / MedicalProfessional
    / Admin) for a freshly‑created User.
    """
    def create(self, user: User, role: str, **extra):
        # role: "patient" | "doctor" | "admin"
        if role == "patient":
            return Patient.objects.create(user=user, **extra)
        elif role == "doctor":
            return MedicalProfessional.objects.create(user=user, **extra)
        elif role == "admin":
            return HealthcareFacilityAdministrator.objects.create(user=user, **extra)
        else:
            raise ValueError(f"Unknown role: {role}")
