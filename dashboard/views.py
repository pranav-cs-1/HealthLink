# views.py
import requests
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from django import forms
from django.shortcuts import get_object_or_404
from .forms import PatientSignUpForm, MedicalProfessionalSignUpForm, AppointmentForm, AdminSignUpForm, \
    PatientAppointmentForm, DoctorAppointmentForm, PrescriptionForm, ReportForm, PatientBillingForm, \
    MedicalProfessionalEditForm, PatientEditForm
from .models import Patient, MedicalProfessional, Appointment, Report, HealthcareFacilityAdministrator
import logging
from .singletons import GeminiClient
from .factories import UserProfileFactory



logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'dashboard/home.html')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

def patient_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if the user is a Patient
            if hasattr(user, 'patient'):
                login(request, user)
                return redirect('patient_dashboard')
            else:
                messages.error(request, "This login is for Patients only.")
                return redirect('patient_login')
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/patient_login.html', {'form': form})

def medical_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if the user is a MedicalProfessional
            if hasattr(user, 'medicalprofessional'):
                login(request, user)
                return redirect('medical_dashboard')
            else:
                messages.error(request, "This login is for Medical Professionals only.")
                return redirect('medical_login')
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/medical_login.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if the user is a HealthcareFacilityAdministrator
            if hasattr(user, 'healthcarefacilityadministrator'):
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "This login is for Administrators only.")
                return redirect('admin_login')
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/admin_login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')


def patient_dashboard(request):
    user = request.user
    try:
        # Retrieve upcoming appointments for this patient
        upcoming_appointments = user.patient.appointment_set.filter(
            appointment_date__gte=timezone.now()
        ).order_by('appointment_date')
        # Retrieve prescriptions for this patient
        prescriptions = user.patient.prescription_set.all().order_by('-created_at')
    except Exception as e:
        upcoming_appointments = []
        prescriptions = []
    context = {
        'upcoming_appointments': upcoming_appointments,
        'prescriptions': prescriptions
    }
    return render(request, 'dashboard/patient_dashboard.html', context)


def medical_dashboard(request):
    user = request.user
    try:
        # Retrieve upcoming appointments for this medical professional
        upcoming_appointments = user.medicalprofessional.appointment_set.filter(
            appointment_date__gte=timezone.now()
        ).order_by('appointment_date')
    except Exception as e:
        upcoming_appointments = []
        # Optionally log the exception e for debugging
    context = {'upcoming_appointments': upcoming_appointments}
    return render(request, 'dashboard/medical_dashboard.html', context)

def admin_new_patient(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Get extra fields from the form
            date_of_birth = form.cleaned_data.get('date_of_birth')
            phone_number = form.cleaned_data.get('phone_number')
            address = form.cleaned_data.get('address')

            # Pass these fields to the UserProfileFactory
            UserProfileFactory().create(
                user=user,
                role="patient",
                date_of_birth=date_of_birth,
                phone_number=phone_number,
                address=address
            )
            messages.success(request, "Patient created successfully!")
            return redirect('admin_patients')
        else:
            # Debug by printing form errors to console (optional)
            print(f"Form errors: {form.errors}")
            messages.error(request, "There was a problem creating the patient. Please correct the errors below.")
    else:
        form = PatientSignUpForm()
    return render(request, 'dashboard/admin_new_patient.html', {'form': form})

def admin_new_doctor(request):
    if request.method == 'POST':
        form = MedicalProfessionalSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a MedicalProfessional profile linked to the user
            MedicalProfessional.objects.create(user=user)
            return redirect('admin_doctors')
    else:
        form = MedicalProfessionalSignUpForm()
    return render(request, 'dashboard/admin_new_doctor.html', {'form': form})

def admin_new_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new appointment
            return redirect('admin_appointments')
    else:
        form = AppointmentForm()
    return render(request, 'dashboard/admin_new_appointment.html', {'form': form})

def admin_settings(request):
    return render(request, 'dashboard/admin_settings.html')

def admin_patients(request):
    patients = Patient.objects.all()
    return render(request, 'dashboard/admin_patients.html', {'patients': patients})

def admin_doctors(request):
    doctors = MedicalProfessional.objects.all()
    return render(request, 'dashboard/admin_doctors.html', {'doctors': doctors})

def admin_appointments(request):
    appointments = Appointment.objects.all()
    return render(request, 'dashboard/admin_appointments.html', {'appointments': appointments})

def admin_reports(request):
    reports = Report.objects.all()
    return render(request, 'dashboard/admin_reports.html', {'reports': reports})

@login_required
def dashboard(request):
    user = request.user
    context = {}
    if hasattr(user, 'patient'):
        context['appointments'] = user.patient.appointment_set.all()
        context['test_results'] = user.patient.testresult_set.all()
        return render(request, 'dashboard/patient_dashboard.html', context)
    elif hasattr(user, 'medicalprofessional'):
        context['appointments'] = user.medicalprofessional.appointment_set.all()
        context['patients'] = [appt.patient for appt in context['appointments']]
        return render(request, 'dashboard/medical_dashboard.html', context)
    elif hasattr(user, 'healthcarefacilityadministrator'):
        return render(request, 'dashboard/admin_dashboard.html', context)
    else:
        return render(request, 'dashboard/home.html')

def admin_dashboard(request):
    # Example context data—adjust as needed
    total_patients = Patient.objects.count()
    total_doctors = MedicalProfessional.objects.count()
    upcoming_appointments = Appointment.objects.order_by('appointment_date')[:5]
    reports = Report.objects.order_by('-date')[:5]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'upcoming_appointments': upcoming_appointments,
        'reports': reports,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Create the User
            # Get extra fields from the form
            date_of_birth = form.cleaned_data.get('date_of_birth')
            phone_number = form.cleaned_data.get('phone_number')
            address = form.cleaned_data.get('address')  # New extraction for address

            # Create the Patient profile linked to the user, including the address
            Patient.objects.create(
                user=user,
                date_of_birth=date_of_birth,
                phone_number=phone_number,
                address=address  # Save the address here
            )
            messages.success(request, "Patient account created successfully! You can now log in.")
            return redirect('patient_login')
    else:
        form = PatientSignUpForm()
    return render(request, 'dashboard/patient_signup.html', {'form': form})

def medical_signup(request):
    if request.method == 'POST':
        form = MedicalProfessionalSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            specialization = form.cleaned_data.get('specialization')
            phone_number = form.cleaned_data.get('phone_number')
            # Create the MedicalProfessional profile
            MedicalProfessional.objects.create(
                user=user,
                specialization=specialization,
                phone_number=phone_number
            )
            messages.success(request, "Medical Professional account created successfully! You can now log in.")
            return redirect('medical_login')
    else:
        form = MedicalProfessionalSignUpForm()
    return render(request, 'dashboard/medical_signup.html', {'form': form})

def admin_signup(request):
    if request.method == 'POST':
        form = AdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            facility_name = form.cleaned_data.get('facility_name')
            phone_number = form.cleaned_data.get('phone_number')
            # Create the Admin profile
            HealthcareFacilityAdministrator.objects.create(
                user=user,
                facility_name=facility_name,
                phone_number=phone_number
            )
            messages.success(request, "Administrator account created successfully! You can now log in.")
            return redirect('admin_login')
    else:
        form = AdminSignUpForm()
    return render(request, 'dashboard/admin_signup.html', {'form': form})

def patient_new_appointment(request):
    # Ensure that only patients can schedule appointments
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Only patients can create appointments.")
        return redirect('dashboard')

    patient = request.user.patient
    if request.method == 'POST':
        form = PatientAppointmentForm(request.POST, patient=patient)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient  # Set the patient from the logged-in user
            appointment.save()
            messages.success(request, "Appointment scheduled successfully!")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "There was a problem scheduling your appointment.")
    else:
        form = PatientAppointmentForm(patient=patient)

    return render(request, 'dashboard/patient_new_appointment.html', {'form': form})

def medical_new_appointment(request):
    # Ensure only doctors can access this view
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only Medical Professionals can create appointments.")
        return redirect('dashboard')

    doctor = request.user.medicalprofessional

    if request.method == 'POST':
        form = DoctorAppointmentForm(request.POST, medical_professional=doctor)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.medical_professional = doctor  # Set the doctor as the logged-in user
            appointment.save()
            messages.success(request, "Appointment created successfully!")
            return redirect('medical_dashboard')
        else:
            messages.error(request, "There was a problem creating the appointment. Please correct the errors below.")
    else:
        form = DoctorAppointmentForm(medical_professional=doctor)

    return render(request, 'dashboard/medical_new_appointment.html', {'form': form})

def medical_new_appointment(request):
    # Ensure only doctors can access this view
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only Medical Professionals can create appointments.")
        return redirect('dashboard')

    doctor = request.user.medicalprofessional

    if request.method == 'POST':
        form = DoctorAppointmentForm(request.POST, medical_professional=doctor)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.medical_professional = doctor  # Set the doctor as the logged-in user
            appointment.save()
            messages.success(request, "Appointment created successfully!")
            return redirect('medical_dashboard')
        else:
            messages.error(request, "There was a problem creating the appointment. Please correct the errors below.")
    else:
        form = DoctorAppointmentForm(medical_professional=doctor)

    return render(request, 'dashboard/medical_new_appointment.html', {'form': form})

@login_required
def medical_new_patient(request):
    # Only allow Medical Professionals to add a patient
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only Medical Professionals can add patients.")
        return redirect('dashboard')

    doctor = request.user.medicalprofessional
    # Exclude patients already assigned to this doctor
    form = AddPatientForm(initial={'patient': None})
    form.fields['patient'].queryset = Patient.objects.exclude(assigned_doctors=doctor)

    if request.method == "POST":
        form = AddPatientForm(request.POST)
        form.fields['patient'].queryset = Patient.objects.exclude(assigned_doctors=doctor)
        if form.is_valid():
            patient = form.cleaned_data['patient']
            doctor.patients.add(patient)
            messages.success(request, f"Patient {patient.user.get_full_name()} added successfully!")
            return redirect('medical_patients')
        else:
            messages.error(request, "There was a problem adding the patient.")

    return render(request, 'dashboard/medical_new_patient.html', {'form': form})


def medical_new_prescription(request):
    # Ensure only medical professionals (doctors) can access this view.
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only Medical Professionals can create prescriptions.")
        return redirect('dashboard')

    doctor = request.user.medicalprofessional

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.medical_professional = doctor
            prescription.save()
            messages.success(request, "Prescription created successfully!")
            return redirect('medical_dashboard')
        else:
            messages.error(request, "There was a problem creating the prescription. Please correct the errors below.")
    else:
        form = PrescriptionForm()

    return render(request, 'dashboard/medical_new_prescription.html', {'form': form})

def generate_drug_description(request):
    medication = request.GET.get('medication')
    if not medication:
        logger.error("No medication provided in request.")
        return JsonResponse({'error': 'No medication provided.'}, status=400)

    try:
        client = GeminiClient()
        description = client.describe_medication(medication)

        logger.debug(f"Generated description for {medication}: {description}")
        return JsonResponse({'description': description})
    except Exception as e:
        logger.exception(f"Error calling Gemini API: {str(e)}")
        fallback_description = f"{medication} is a medication used to treat specific conditions."

        debug_info = {"exception": str(e)}

        if settings.DEBUG:
            return JsonResponse({'description': fallback_description, 'debug': debug_info})
        else:
            return JsonResponse({'description': fallback_description})


# Add these new view functions to the existing views.py file

def medical_new_report(request):
    # Ensure only medical professionals can create reports
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only medical professionals can create reports.")
        return redirect('medical_dashboard')

    doctor = request.user.medicalprofessional

    # Debug: Count appointments and patients for this doctor
    appointments_count = Appointment.objects.filter(
        medical_professional=doctor
    ).count()

    patients_count = Patient.objects.filter(
        appointment__medical_professional=doctor
    ).distinct().count()

    if request.method == 'POST':
        form = ReportForm(request.POST, medical_professional=doctor)
        if form.is_valid():
            report = form.save(commit=False)
            report.medical_professional = doctor
            report.save()
            messages.success(request, "Report created successfully!")
            return redirect('medical_dashboard')
        else:
            messages.error(request, "There was a problem creating the report.")
    else:
        form = ReportForm(medical_professional=doctor)

    context = {
        'form': form,
        'debug_info': {
            'appointments_count': appointments_count,
            'patients_count': patients_count,
        }
    }
    return render(request, 'dashboard/medical_new_report.html', context)

def patient_view_reports(request):
    # Ensure only patients can view their own reports
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Only patients can view their reports.")
        return redirect('dashboard')

    patient = request.user.patient
    reports = Report.objects.filter(patient=patient).order_by('-date')

    return render(request, 'dashboard/patient_reports.html', {'reports': reports})


def medical_view_reports(request):
    # Ensure only medical professionals can view reports they've created
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only medical professionals can view this page.")
        return redirect('dashboard')

    doctor = request.user.medicalprofessional
    reports = Report.objects.filter(medical_professional=doctor).order_by('-date')

    return render(request, 'dashboard/medical_reports.html', {'reports': reports})


def report_detail(request, report_id):
    # This view allows both patients and doctors to view a specific report
    try:
        report = Report.objects.get(id=report_id)

        # Check permissions - only the patient or the doctor who created the report can view it
        if hasattr(request.user, 'patient') and request.user.patient == report.patient:
            # Patient viewing their own report
            return render(request, 'dashboard/report_detail.html', {'report': report})
        elif hasattr(request.user,
                     'medicalprofessional') and request.user.medicalprofessional == report.medical_professional:
            # Doctor viewing a report they created
            return render(request, 'dashboard/report_detail.html', {'report': report})
        else:
            messages.error(request, "You don't have permission to view this report.")
            return redirect('dashboard')

    except Report.DoesNotExist:
        messages.error(request, "Report not found.")
        return redirect('dashboard')

class AddPatientForm(forms.Form):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        label="Select a patient",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

@login_required
def medical_new_report(request):
    # Ensure only medical professionals can create reports
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only medical professionals can create reports.")
        return redirect('medical_dashboard')

    doctor = request.user.medicalprofessional

    # Debug: Count patients for this doctor
    appointment_patients = Patient.objects.filter(
        appointment__medical_professional=doctor
    ).distinct().count()

    assigned_patients = doctor.patients.count()

    if request.method == 'POST':
        form = ReportForm(request.POST, medical_professional=doctor)
        if form.is_valid():
            report = form.save(commit=False)
            report.medical_professional = doctor
            report.save()
            messages.success(request, "Report created successfully!")
            return redirect('medical_dashboard')
        else:
            messages.error(request, "There was a problem creating the report.")
    else:
        form = ReportForm(medical_professional=doctor)

    context = {
        'form': form,
        'debug_info': {
            'appointment_patients': appointment_patients,
            'assigned_patients': assigned_patients,
        }
    }
    return render(request, 'dashboard/medical_new_report.html', context)


@login_required
def medical_patients(request):
    # Only allow Medical Professionals to view patients
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only Medical Professionals can view patients.")
        return redirect('dashboard')
    doctor = request.user.medicalprofessional
    patients = doctor.patients.all()
    return render(request, 'dashboard/medical_patients.html', {'patients': patients})

@login_required
def medical_patient_detail(request, patient_id):
    # Only allow Medical Professionals to view patient details
    if not hasattr(request.user, 'medicalprofessional'):
        messages.error(request, "Only Medical Professionals can view patient details.")
        return redirect('dashboard')
    doctor = request.user.medicalprofessional
    try:
        # Ensure the patient is assigned to the doctor
        patient = doctor.patients.get(id=patient_id)
    except Patient.DoesNotExist:
        messages.error(request, "Patient not found or not associated with you.")
        return redirect('medical_patients')
    # Retrieve the patient’s reports and prescriptions
    reports = patient.reports.all().order_by('-date')
    prescriptions = patient.prescription_set.all().order_by('-created_at')
    return render(request, 'dashboard/medical_patient_detail.html', {
        'patient': patient,
        'reports': reports,
        'prescriptions': prescriptions,
    })

@login_required
def patient_appointments(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Only patients can view appointments.")
        return redirect('dashboard')
    patient = request.user.patient
    # Retrieve all appointments for the patient, sorted by date/time.
    appointments = patient.appointment_set.all().order_by('appointment_date')
    return render(request, 'dashboard/patient_appointments.html', {'appointments': appointments})


@login_required
def patient_edit_appointment(request, appointment_id):
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Only patients can modify appointments.")
        return redirect('dashboard')
    patient = request.user.patient
    # Ensure the appointment belongs to the logged in patient
    appointment = get_object_or_404(patient.appointment_set, id=appointment_id)

    if request.method == "POST":
        # We use the same PatientAppointmentForm, supplying the instance.
        form = PatientAppointmentForm(request.POST, instance=appointment, patient=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully!")
            return redirect('patient_appointments')
        else:
            messages.error(request, "Error updating the appointment. Please correct the errors below.")
    else:
        form = PatientAppointmentForm(instance=appointment, patient=patient)

    return render(request, 'dashboard/patient_edit_appointment.html', {
        'form': form,
        'appointment': appointment
    })

@login_required
def patient_delete_appointment(request, appointment_id):
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Only patients can delete appointments.")
        return redirect('dashboard')

    patient = request.user.patient
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")
        return redirect('patient_appointments')

    messages.error(request, "Invalid request method.")
    return redirect('patient_appointments')

@login_required
def patient_prescriptions(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Only patients can view prescriptions.")
        return redirect('dashboard')

    patient = request.user.patient
    prescriptions = patient.prescription_set.all().order_by('-created_at')
    return render(request, 'dashboard/patient_prescriptions.html', {'prescriptions': prescriptions})

class PharmacySearchForm(forms.Form):
    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter address to find nearby pharmacies'
        })
    )

@login_required
def find_pharmacy(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Only patients can use this feature.")
        return redirect('dashboard')

    results = None
    if request.method == 'POST':
        form = PharmacySearchForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            # We'll pass the address to the template and let
            # the JavaScript handle the Nominatim API call
            results = {
                'address': address,
            }
    else:
        # Pre-fill with patient's address if available
        initial_data = {}
        if request.user.patient.address:
            initial_data['address'] = request.user.patient.address
        form = PharmacySearchForm(initial=initial_data)

    return render(request, 'dashboard/find_pharmacy.html', {'form': form, 'results': results})

def patient_billing(request):
    if not hasattr(request.user, 'patient') and not hasattr(request.user, 'administrator'):
        messages.error(request, "Only patients and admins can update billing information.")
        return redirect('dashboard')

    user = request.user
    patient = get_object_or_404(Patient, user=user)  # get the patient associated with this user

    if request.method == 'POST':
        form = PatientBillingForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # optionally also update fields in the patient object if needed
            patient.address = form.cleaned_data.get('address')
            patient.phone_number = form.cleaned_data.get('phone_number')
            patient.save()
            return redirect('patient_billing')
    else:
        form = PatientBillingForm(instance=user, initial={
            'address': patient.address,
            'phone_number': patient.phone_number,
        })

    context = {
        'form': form,
        'current_info': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'address': patient.address,
            'phone_number': patient.phone_number,
            'date_of_birth': patient.date_of_birth,
        }
    }

    return render(request, 'dashboard/patient_billing.html', context)

@login_required
def admin_view_patient(request, patient_id):
    # Ensure only admins can access this view
    if not hasattr(request.user, 'healthcarefacilityadministrator'):
        messages.error(request, "Only administrators can view patient details.")
        return redirect('admin_dashboard')

    patient = get_object_or_404(Patient, id=patient_id)
    # Get related data for the patient
    appointments = patient.appointment_set.all().order_by('-appointment_date')
    prescriptions = patient.prescription_set.all().order_by('-created_at')
    reports = patient.reports.all().order_by('-date')

    context = {
        'patient': patient,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'reports': reports
    }
    return render(request, 'dashboard/admin_view_patient.html', context)


@login_required
def admin_edit_patient(request, patient_id):
    # Ensure only admins can access this view
    if not hasattr(request.user, 'healthcarefacilityadministrator'):
        messages.error(request, "Only administrators can edit patient details.")
        return redirect('admin_dashboard')

    patient = get_object_or_404(Patient, id=patient_id)
    user = patient.user

    if request.method == 'POST':
        # Create a form instance with POST data
        form = PatientEditForm(request.POST, instance=user)
        if form.is_valid():
            # Save the user form
            form.save()
            # Update additional patient fields
            patient.date_of_birth = form.cleaned_data.get('date_of_birth')
            patient.phone_number = form.cleaned_data.get('phone_number')
            patient.address = form.cleaned_data.get('address')
            patient.save()
            messages.success(request, "Patient information updated successfully.")
            return redirect('admin_patients')
    else:
        # Pre-populate form with existing data
        form = PatientEditForm(instance=user, initial={
            'date_of_birth': patient.date_of_birth,
            'phone_number': patient.phone_number,
            'address': patient.address
        })

    context = {
        'form': form,
        'patient': patient,
        'current_info': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'date_of_birth': patient.date_of_birth,
            'phone_number': patient.phone_number,
            'address': patient.address
        }
    }

    return render(request, 'dashboard/admin_edit_patient.html', context)


@login_required
def admin_edit_doctor(request, doctor_id):
    # Ensure only admins can access this view
    if not hasattr(request.user, 'healthcarefacilityadministrator'):
        messages.error(request, "Only administrators can edit doctor details.")
        return redirect('admin_dashboard')

    doctor = get_object_or_404(MedicalProfessional, id=doctor_id)
    user = doctor.user

    if request.method == 'POST':
        # Create a form instance with POST data
        form = MedicalProfessionalEditForm(request.POST, instance=user)
        if form.is_valid():
            # Save the user form
            form.save()
            # Update additional doctor fields
            doctor.specialization = form.cleaned_data.get('specialization')
            doctor.phone_number = form.cleaned_data.get('phone_number')
            doctor.save()
            messages.success(request, "Doctor information updated successfully.")
            return redirect('admin_doctors')
    else:
        # Pre-populate form with existing data
        form = MedicalProfessionalEditForm(instance=user, initial={
            'specialization': doctor.specialization,
            'phone_number': doctor.phone_number
        })

    context = {
        'form': form,
        'doctor': doctor,
        'current_info': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'specialization': doctor.specialization,
            'phone_number': doctor.phone_number
        }
    }

    return render(request, 'dashboard/admin_edit_doctor.html', context)


@login_required
def admin_view_doctor(request, doctor_id):
    # Ensure only admins can access this view
    if not hasattr(request.user, 'healthcarefacilityadministrator'):
        messages.error(request, "Only administrators can view doctor details.")
        return redirect('admin_dashboard')

    doctor = get_object_or_404(MedicalProfessional, id=doctor_id)
    # Get related data for the doctor
    patients = doctor.patients.all()
    appointments = doctor.appointment_set.all().order_by('-appointment_date')
    reports = Report.objects.filter(medical_professional=doctor).order_by('-date')

    context = {
        'doctor': doctor,
        'patients': patients,
        'appointments': appointments,
        'reports': reports
    }
    return render(request, 'dashboard/admin_view_doctor.html', context)


@login_required
def admin_delete_patient(request, patient_id):
    # Ensure only admins can access this view
    if not hasattr(request.user, 'healthcarefacilityadministrator'):
        messages.error(request, "Only administrators can delete patients.")
        return redirect('admin_dashboard')

    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        # Get the user associated with the patient
        user = patient.user
        # Delete the user (this will cascade delete related records based on model setup)
        user.delete()  # This will also delete the patient due to the CASCADE relationship
        messages.success(request, "Patient has been deleted successfully.")
        return redirect('admin_patients')

    return render(request, 'dashboard/admin_confirm_delete_patient.html', {'patient': patient})


@login_required
def admin_delete_doctor(request, doctor_id):
    # Ensure only admins can access this view
    if not hasattr(request.user, 'healthcarefacilityadministrator'):
        messages.error(request, "Only administrators can delete doctors.")
        return redirect('admin_dashboard')

    doctor = get_object_or_404(MedicalProfessional, id=doctor_id)

    if request.method == 'POST':
        # Get the user associated with the doctor
        user = doctor.user
        # Delete the user (this will cascade delete the doctor record)
        user.delete()
        messages.success(request, "Doctor has been deleted successfully.")
        return redirect('admin_doctors')

    return render(request, 'dashboard/admin_confirm_delete_doctor.html', {'doctor': doctor})

@login_required
def admin_edit_appointment(request, appointment_id):
    # only admins
    if not hasattr(request.user, 'healthcarefacilityadministrator'):
        messages.error(request, "Only administrators can edit appointments.")
        return redirect('admin_appointments')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('admin_appointments')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'dashboard/admin_edit_appointment.html', {
        'form': form,
        'appointment': appointment
    })

@login_required
def admin_delete_appointment(request, appointment_id):
    # only admins
    if not hasattr(request.user, 'healthcarefacilityadministrator'):
        messages.error(request, "Only administrators can delete appointments.")
        return redirect('admin_appointments')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")
        return redirect('admin_appointments')

    # if GET, show a confirmation page (optional)
    return render(request, 'dashboard/admin_confirm_delete_appointment.html', {
        'appointment': appointment
    })