from django.urls import path
from .views import patient_data, dashboard, export_patient_data, get_filter_options

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('api/patient-data/', patient_data, name='patient-data'),
    path('api/export-patient-data/', export_patient_data, name='export_patient_data'),
    path('api/filter-options/', get_filter_options, name='get_filter_options'),
]

