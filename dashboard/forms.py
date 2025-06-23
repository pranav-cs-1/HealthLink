# dashboard/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Appointment, Report, Prescription, Patient
from django.utils import timezone


class PatientSignUpForm(UserCreationForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2'
        ]

class ReportForm(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())

    class Meta:
        model = Report
        fields = ['patient', 'title', 'summary']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        # Allow passing the doctor to the form to filter patients
        self.medical_professional = kwargs.pop('medical_professional', None)
        super().__init__(*args, **kwargs)

        # Show all patients if no doctor is provided
        if self.medical_professional:
            # Try to get patients from appointments first
            patients_with_appointments = Patient.objects.filter(
                appointment__medical_professional=self.medical_professional
            ).distinct()

            # If no patients have appointments, try to get from the M2M relationship
            if not patients_with_appointments.exists():
                patients_with_appointments = self.medical_professional.patients.all()

            # If still no patients, show all patients as a fallback
            if not patients_with_appointments.exists():
                self.fields['patient'].help_text = "No patients are associated with you. Showing all patients."
            else:
                self.fields['patient'].queryset = patients_with_appointments


class MedicalProfessionalSignUpForm(UserCreationForm):
    specialization = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class AdminSignUpForm(UserCreationForm):
    facility_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    class Meta:
        model = Appointment
        fields = ['patient', 'medical_professional', 'appointment_date', 'reason']

class PatientAppointmentForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Appointment
        # Exclude patient because it will be set from the logged-in user
        fields = ['medical_professional', 'appointment_date', 'reason']

    def __init__(self, *args, **kwargs):
        # Expect the current patient instance to be passed in
        self.patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date and appointment_date <= timezone.now():
            raise forms.ValidationError("The appointment date must be in the future.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        doctor = cleaned_data.get('medical_professional')
        if appointment_date and doctor and self.patient:
            # Check if the doctor already has an appointment at that time
            if Appointment.objects.filter(
                    medical_professional=doctor,
                    appointment_date=appointment_date
            ).exists():
                raise forms.ValidationError("This doctor is not available at that time.")

            # Check if the patient already has an appointment at that time
            if Appointment.objects.filter(
                    patient=self.patient,
                    appointment_date=appointment_date
            ).exists():
                raise forms.ValidationError("You already have an appointment at that time.")
        return cleaned_data


class DoctorAppointmentForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Appointment
        # The form includes the patient, appointment_date, and reason.
        # The medical_professional field will be set in the view.
        fields = ['patient', 'appointment_date', 'reason']

    def __init__(self, *args, **kwargs):
        # Expect the current medical professional to be passed in.
        self.medical_professional = kwargs.pop('medical_professional', None)
        super().__init__(*args, **kwargs)

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date and appointment_date <= timezone.now():
            raise forms.ValidationError("The appointment date must be in the future.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        patient = cleaned_data.get('patient')
        if appointment_date and patient and self.medical_professional:
            # Check if the doctor already has an appointment at that time.
            if Appointment.objects.filter(
                    medical_professional=self.medical_professional,
                    appointment_date=appointment_date
            ).exists():
                raise forms.ValidationError("You already have an appointment at that time.")
            # Check if the selected patient already has an appointment at that time.
            if Appointment.objects.filter(
                    patient=patient,
                    appointment_date=appointment_date
            ).exists():
                raise forms.ValidationError("This patient already has an appointment at that time.")
        return cleaned_data

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        # The doctor’s account is set in the view so we only include the patient, medication, and description.
        fields = ['patient', 'medication_name', 'description']

class PatientBillingForm(UserChangeForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your phone number',
            'class': 'form-control'
        })
    )
    address = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your address',
            'class': 'form-control'
        })
    )

    class Meta(UserChangeForm.Meta):
        model = User  # Replace with the actual model that stores patient data
        fields = ['address', 'phone_number', 'email', 'first_name', 'last_name']  # List fields you want to allow the patient to update

        # Optional: Customizing widgets, like making some fields more user-friendly
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Enter your address', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            self.fields.pop('password')
    # Optional: Custom validation for some fields if needed
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # You can add a validation rule for phone numbers (e.g., check length, format, etc.)
        if len(phone_number) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits.")
        return phone_number

    def clean_email(self):
        return self.cleaned_data.get('email')

class PatientEditForm(UserChangeForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field from the form
        if 'password' in self.fields:
            self.fields.pop('password')


class MedicalProfessionalEditForm(UserChangeForm):
    specialization = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field from the form
        if 'password' in self.fields:
            self.fields.pop('password')