from django.test import TestCase
from django.urls import reverse
from .models import Patient
from rest_framework.test import APIClient

class PatientFilterTests(TestCase):

    def setUp(self):
        # Set up test data for the Patient model, including age
        Patient.objects.create(
            patient_id="1", diagnosis="Hypertension", gender="Male", age=45, lab_results=150.0,
            date="2024-01-15", visit_type="Routine Checkup", outcome="Admitted"
        )
        Patient.objects.create(
            patient_id="2", diagnosis="Asthma", gender="Female", age=32, lab_results=130.0,
            date="2024-02-10", visit_type="Emergency", outcome="Discharged"
        )
        Patient.objects.create(
            patient_id="3", diagnosis="Hypertension", gender="Female", age=50, lab_results=140.0,
            date="2024-03-20", visit_type="Routine Checkup", outcome="Admitted"
        )

        self.client = APIClient()

    def test_filter_by_diagnosis(self):
        # Test filtering by diagnosis
        response = self.client.get(reverse('patient-data'), {'diagnosis': 'Hypertension'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)  # Expecting 2 entries with Hypertension

    def test_filter_by_gender(self):
        # Test filtering by gender
        response = self.client.get(reverse('patient-data'), {'gender': 'Male'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)  # Expecting 1 Male entry

    def test_filter_by_visit_type(self):
        # Test filtering by visit type
        response = self.client.get(reverse('patient-data'), {'visit_type': 'Emergency'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)  # Expecting 1 Emergency entry

    def test_filter_by_multiple_criteria(self):
        # Test filtering by multiple criteria (diagnosis + gender)
        response = self.client.get(reverse('patient-data'), {'diagnosis': 'Hypertension', 'gender': 'Female'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)  # Expecting 1 Female Hypertension entry

    def test_filter_by_date_range(self):
        # Test filtering by date range
        response = self.client.get(reverse('patient-data'), {'from_date': '2024-01-01', 'to_date': '2024-02-01'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)  # Expecting 1 entry in the date range

    def test_export_patient_data(self):
        # Test CSV export functionality
        response = self.client.get(reverse('export_patient_data'), {'diagnosis': 'Hypertension'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment; filename="patient_data.csv"', response['Content-Disposition'])
        self.assertEqual(response.get('content-type'), 'text/csv')
        # Check CSV content contains expected data
        content = response.content.decode('utf-8')
        self.assertIn("Hypertension", content)

    def test_get_filter_options(self):
        # Test getting filter options for diagnosis, gender, and visit type
        response = self.client.get(reverse('get_filter_options'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('Hypertension', data['diagnosis_options'])
        self.assertIn('Female', data['gender_options'])
        self.assertIn('Routine Checkup', data['visit_type_options'])


class PatientModelTests(TestCase):
    
    def setUp(self):
        # Create some patients for testing aggregation and filtering
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

    def test_average_lab_results(self):
        patients = Patient.objects.all()
        total_lab_results = sum(patient.lab_results for patient in patients)
        avg_lab_results = total_lab_results / len(patients)
        
        self.assertAlmostEqual(avg_lab_results, 133.33, places=2)  # Adjust based on expected results

    def test_adverse_outcomes_count(self):
        # Check that adverse outcomes (e.g., 'Admitted') are correctly counted
        admitted_count = Patient.objects.filter(outcome='Admitted').count()
        self.assertEqual(admitted_count, 2)  # Expecting 2 patients with 'Admitted' outcome