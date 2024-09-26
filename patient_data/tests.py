from django.test import TestCase
from django.urls import reverse
from .models import Patient
from rest_framework.test import APIClient

class PatientFilterTests(TestCase):

    def setUp(self):
        patients = [
            # Hypertension cases
            {"patient_id": "1", "diagnosis": "Hypertension", "gender": "Male", "age": 45, "lab_results": 150.0, "date": "2024-01-15", "visit_type": "Routine Checkup", "outcome": "Admitted"},
            {"patient_id": "2", "diagnosis": "Hypertension", "gender": "Female", "age": 50, "lab_results": 140.0, "date": "2024-03-20", "visit_type": "Routine Checkup", "outcome": "Admitted"},
            {"patient_id": "3", "diagnosis": "Hypertension", "gender": "Male", "age": 60, "lab_results": 130.0, "date": "2024-04-05", "visit_type": "Emergency", "outcome": "Discharged"},

            # Asthma cases
            {"patient_id": "4", "diagnosis": "Asthma", "gender": "Female", "age": 30, "lab_results": 120.0, "date": "2024-02-10", "visit_type": "Emergency", "outcome": "Discharged"},
            {"patient_id": "5", "diagnosis": "Asthma", "gender": "Male", "age": 25, "lab_results": 115.0, "date": "2024-05-12", "visit_type": "Routine Checkup", "outcome": "Admitted"},

            # Diabetes cases
            {"patient_id": "6", "diagnosis": "Diabetes", "gender": "Female", "age": 60, "lab_results": 140.0, "date": "2024-05-10", "visit_type": "Follow-up", "outcome": "Admitted"},
            {"patient_id": "7", "diagnosis": "Diabetes", "gender": "Female", "age": 70, "lab_results": 145.0, "date": "2024-06-15", "visit_type": "Follow-up", "outcome": "Discharged"},

            # Cardiovascular Disease cases
            {"patient_id": "8", "diagnosis": "Cardiovascular Disease", "gender": "Male", "age": 65, "lab_results": 160.0, "date": "2024-07-01", "visit_type": "Emergency", "outcome": "Admitted"},
            {"patient_id": "9", "diagnosis": "Cardiovascular Disease", "gender": "Female", "age": 75, "lab_results": 155.0, "date": "2024-08-10", "visit_type": "Routine Checkup", "outcome": "Discharged"},

            # COVID-19 cases
            {"patient_id": "10", "diagnosis": "COVID-19", "gender": "Female", "age": 55, "lab_results": 150.0, "date": "2024-01-10", "visit_type": "Emergency", "outcome": "Admitted"},
            {"patient_id": "11", "diagnosis": "COVID-19", "gender": "Male", "age": 40, "lab_results": 110.0, "date": "2024-02-05", "visit_type": "Follow-up", "outcome": "Discharged"},

            # Hypertension cases in different date ranges
            {"patient_id": "12", "diagnosis": "Hypertension", "gender": "Female", "age": 42, "lab_results": 135.0, "date": "2024-09-01", "visit_type": "Emergency", "outcome": "Discharged"},
            {"patient_id": "13", "diagnosis": "Hypertension", "gender": "Male", "age": 55, "lab_results": 128.0, "date": "2024-10-12", "visit_type": "Routine Checkup", "outcome": "Admitted"},

            # Additional test cases for edge scenarios
            {"patient_id": "14", "diagnosis": "Diabetes", "gender": "Male", "age": 61, "lab_results": 155.0, "date": "2024-11-03", "visit_type": "Routine Checkup", "outcome": "Admitted"},
            {"patient_id": "15", "diagnosis": "Asthma", "gender": "Female", "age": 28, "lab_results": 118.0, "date": "2024-11-05", "visit_type": "Emergency", "outcome": "Discharged"},
        ]

        # Create patients from the dataset
        for patient in patients:
            Patient.objects.create(**patient)

        self.client = APIClient()

    def test_filter_by_diagnosis(self):
        response = self.client.get(reverse('patient-data'), {'diagnosis[]': ['Hypertension']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)  # 5 patients with Hypertension

    def test_filter_by_gender(self):
        response = self.client.get(reverse('patient-data'), {'gender[]': ['Female']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 8)  # 8 Female patients

    def test_filter_by_visit_type(self):
        response = self.client.get(reverse('patient-data'), {'visit_type[]': ['Emergency']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 6)  # 6 Emergency cases

    def test_filter_by_multiple_criteria(self):
        response = self.client.get(reverse('patient-data'), {'diagnosis[]': ['Hypertension'], 'gender[]': ['Female']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)  # 2 Female Hypertension patients

    def test_filter_by_date_range(self):
        response = self.client.get(reverse('patient-data'), {'from_date': '2024-01-01', 'to_date': '2024-01-31'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)  # 2 entries within January 2024

    def test_filter_by_combined_criteria(self):
        response = self.client.get(reverse('patient-data'), {
            'gender[]': ['Female'], 
            'from_date': '2024-01-01', 
            'to_date': '2024-12-31'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 8)  # 8 Female patients in 2024

    def test_export_patient_data(self):
        response = self.client.get(reverse('export_patient_data'), {'diagnosis': 'Hypertension'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment; filename="patient_data.csv"', response['Content-Disposition'])
        self.assertEqual(response.get('content-type'), 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn("Hypertension", content)

    def test_get_filter_options(self):
        response = self.client.get(reverse('get_filter_options'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('Hypertension', data['diagnosis_options'])
        self.assertIn('Female', data['gender_options'])
        self.assertIn('Routine Checkup', data['visit_type_options'])


class PatientModelTests(TestCase):
    
    def setUp(self):
        # More diverse set of patients for testing aggregation and filtering
        Patient.objects.create(
            patient_id="1", diagnosis="COVID-19", gender="Male", age=40, lab_results=110.0,
            date="2024-01-01", visit_type="Routine Checkup", outcome="Admitted"
        )
        Patient.objects.create(
            patient_id="2", diagnosis="COVID-19", gender="Female", age=55, lab_results=150.0,
            date="2024-01-10", visit_type="Emergency", outcome="Admitted"
        )
        Patient.objects.create(
            patient_id="3", diagnosis="Hypertension", gender="Male", age=60, lab_results=140.0,
            date="2024-02-15", visit_type="Routine Checkup", outcome="Discharged"
        )
        Patient.objects.create(
            patient_id="4", diagnosis="Hypertension", gender="Male", age=55, lab_results=130.0,
            date="2024-03-01", visit_type="Emergency", outcome="Discharged"
        )

    def test_average_lab_results(self):
        patients = Patient.objects.all()
        total_lab_results = sum(patient.lab_results for patient in patients)