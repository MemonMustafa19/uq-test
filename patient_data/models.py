from django.db import models

class Patient(models.Model):
    patient_id = models.CharField(max_length=100, primary_key=True, db_column='PatientID')
    date = models.DateField(db_column='Date')
    age = models.IntegerField(db_column='Age')
    gender = models.CharField(max_length=10, db_column='Gender')
    diagnosis = models.CharField(max_length=100, db_column='Diagnosis')
    lab_results = models.FloatField(db_column='LabResults')
    medication = models.CharField(max_length=100, null=True, blank=True, db_column='Medication')
    visit_type = models.CharField(max_length=50, db_column='VisitType')
    outcome = models.CharField(max_length=50, db_column='Outcome')

    class Meta:
        db_table = 'patient_data'
