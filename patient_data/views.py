from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer

@api_view(['GET'])
def patient_data(request):
    diagnosis = request.GET.get('diagnosis')
    gender = request.GET.get('gender')
    visit_type = request.GET.get('visit_type')

    patients = Patient.objects.all()

    if diagnosis:
        patients = patients.filter(diagnosis=diagnosis)
    if gender:
        patients = patients.filter(gender=gender)
    if visit_type:
        patients = patients.filter(visit_type=visit_type)

    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)

from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
def dashboard(request):
    return render(request, 'patient_data/dashboard.html')

import csv
from django.http import HttpResponse

@api_view(['GET'])
def export_patient_data(request):
    diagnosis = request.GET.get('diagnosis')
    gender = request.GET.get('gender')
    visit_type = request.GET.get('visit_type')

    patients = Patient.objects.all()

    if diagnosis:
        patients = patients.filter(diagnosis=diagnosis)
    if gender:
        patients = patients.filter(gender=gender)
    if visit_type:
        patients = patients.filter(visit_type=visit_type)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patient_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Patient ID', 'Date', 'Age', 'Gender', 'Diagnosis', 'Lab Results', 'Medication', 'Visit Type', 'Outcome'])

    for patient in patients:
        writer.writerow([patient.patient_id, patient.date, patient.age, patient.gender, patient.diagnosis, patient.lab_results, patient.medication, patient.visit_type, patient.outcome])

    return response

@api_view(['GET'])
def get_filter_options(request):
    diagnosis_options = Patient.objects.values_list('diagnosis', flat=True).distinct()
    gender_options = Patient.objects.values_list('gender', flat=True).distinct()
    visit_type_options = Patient.objects.values_list('visit_type', flat=True).distinct()

    return Response({
        'diagnosis_options': diagnosis_options,
        'gender_options': gender_options,
        'visit_type_options': visit_type_options,
    })
