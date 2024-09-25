let patientData = [];
let labResultsChart;

// Initialize DataTable and load data when the document is ready
$(document).ready(function() {
    // Initialize Select2 for multi-select dropdowns
    $('#diagnosisFilter').select2({ placeholder: 'Select Diagnosis' });
    $('#genderFilter').select2({ placeholder: 'Select Gender' });
    $('#visitTypeFilter').select2({ placeholder: 'Select Visit Type' });

    // Load dynamic filter options for Diagnosis, Gender, and Visit Type
    loadFilterOptions();

    // Initialize DataTable
    var table = $('#patientTable').DataTable();

    // Load patient data into table and chart
    loadTable();

    // Apply filters when button is clicked
    $('#applyFilters').on('click', function() {
        applyFilters(table);
    });

    // Export data on button click
    $('#exportData').on('click', function() {
        exportData();
    });
});

// Function to load dynamic filter options
function loadFilterOptions() {
    $.ajax({
        url: '/api/filter-options/',  // API endpoint to get filter options
        method: 'GET',
        success: function(data) {
            populateSelect('#diagnosisFilter', data.diagnosis_options);
            populateSelect('#genderFilter', data.gender_options);
            populateSelect('#visitTypeFilter', data.visit_type_options);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching filter options:', error);
        }
    });
}

// Populate select dropdown with options dynamically
function populateSelect(selector, options) {
    var select = $(selector);
    select.empty(); // Clear existing options
    $.each(options, function(index, value) {
        select.append($('<option>', { value: value, text: value }));
    });
}

// Load patient data from API and populate table and chart
function loadTable() {
    $.ajax({
        url: '/api/patient-data/',  // Adjust this URL to match your Django view
        method: 'GET',
        success: function(data) {
            console.log('Data received:', data);
            patientData = data.filter(patient => patient.date && patient.lab_results);

            // Populate DataTable with patient data
            const table = $('#patientTable').DataTable();
            table.clear();

            patientData.forEach(patient => {
                table.row.add([
                    patient.patient_id,
                    patient.date,
                    patient.age,
                    patient.gender,
                    patient.diagnosis,
                    patient.lab_results,
                    patient.medication,
                    patient.visit_type,
                    patient.outcome
                ]).draw();
            });

            // Initialize or update the chart and metrics
            updateChart(patientData);
            calculateMetrics(patientData);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching data:', error);
        }
    });
}

// Update the chart with the provided data
function updateChart(dataArray) {
    const ctx = document.getElementById('labResultsChart').getContext('2d');

    // Sort the dataArray by date in ascending order
    const sortedData = dataArray.slice().sort((a, b) => new Date(a.date) - new Date(b.date));

    // Extract the labels (dates) and data (lab results) from the sorted data
    const labels = sortedData.map(item => new Date(item.date)); // Convert strings to Date objects
    const labResults = sortedData.map(item => item.lab_results);

    if (labResultsChart) {
        // If the chart already exists, update the data
        labResultsChart.data.labels = labels;
        labResultsChart.data.datasets[0].data = labResults;
        labResultsChart.update();
    } else {
        // If the chart does not exist, create a new one
        labResultsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Lab Results Over Time',
                    data: labResults,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 1,
                    fill: true,
                    tension: 0  // This ensures the lines are straight (no smoothing)
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time', // Set x-axis to time scale
                        time: {
                            unit: 'day', // Show day-level granularity
                            tooltipFormat: 'dd/MM/yyyy', // Tooltip format (Australian)
                            displayFormats: {
                                day: 'dd/MM/yyyy',  // X-axis format showing DD/MM/YYYY
                                month: 'MM/yyyy',   // For months, show MM/YYYY
                                year: 'yyyy'        // For years, show only the year
                            }
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Lab Results'
                        },
                        beginAtZero: false
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
}

// Calculate and display key metrics on the dashboard
function calculateMetrics(dataArray) {
    let diagnosisCounts = {};  // Store number of visits by diagnosis
    let adverseOutcomesByDiagnosis = {};  // Store adverse outcomes by diagnosis
    let labResultsByDiagnosis = {};  // Store total lab results by diagnosis

    dataArray.forEach(function(item) {
        // Track the number of visits by diagnosis
        if (item.diagnosis) {
            if (!diagnosisCounts[item.diagnosis]) {
                diagnosisCounts[item.diagnosis] = 0;
                adverseOutcomesByDiagnosis[item.diagnosis] = { total: 0, adverse: 0 };
                labResultsByDiagnosis[item.diagnosis] = { totalLabResults: 0, count: 0 };
            }
            diagnosisCounts[item.diagnosis]++;
            
            // Track lab results by diagnosis
            labResultsByDiagnosis[item.diagnosis].totalLabResults += item.lab_results;
            labResultsByDiagnosis[item.diagnosis].count++;

            // Track adverse outcomes for each diagnosis
            if (item.outcome && item.outcome.toLowerCase() === 'admitted') {
                adverseOutcomesByDiagnosis[item.diagnosis].adverse++;
            }
            adverseOutcomesByDiagnosis[item.diagnosis].total++;
        }
    });

    // Calculate average lab results and adverse outcome percentage
    let averageLabResultsByDiagnosis = '';
    let adverseOutcomePercentageByDiagnosis = '';
    let numberOfVisitsByDiagnosis = ''; // New variable for visit counts

    // Get top 3 diagnoses based on number of visits
    let topDiagnoses = Object.keys(diagnosisCounts)
        .sort((a, b) => diagnosisCounts[b] - diagnosisCounts[a]) // Sort by number of visits
        .slice(0, 3); // Get top 3 diagnoses

    for (const diagnosis in labResultsByDiagnosis) {
        const avgLabResults = (labResultsByDiagnosis[diagnosis].totalLabResults / labResultsByDiagnosis[diagnosis].count).toFixed(2);
        const adverseOutcomePercentage = ((adverseOutcomesByDiagnosis[diagnosis].adverse / adverseOutcomesByDiagnosis[diagnosis].total) * 100).toFixed(2);

        // Format the average lab results
        averageLabResultsByDiagnosis += `<strong>${diagnosis}:</strong> ${avgLabResults}<br>`;
        
        // Format the adverse outcome percentage (fixing the double % issue)
        adverseOutcomePercentageByDiagnosis += `<strong>${diagnosis}:</strong> ${adverseOutcomePercentage}%<br>`;
        
        // Format the number of visits by diagnosis (new)
        numberOfVisitsByDiagnosis += `<strong>${diagnosis}:</strong> ${diagnosisCounts[diagnosis]} visits<br>`;
    }

    // Update the metrics on the page
    $('#averageLabResults').html(averageLabResultsByDiagnosis);
    $('#adverseOutcomes').html(adverseOutcomePercentageByDiagnosis);
    $('#visitsByDiagnosis').html(numberOfVisitsByDiagnosis);  // Updated with the number of visits
}

// Apply the selected filters to the table and chart
function applyFilters(table) {
    const selectedDiagnosis = $('#diagnosisFilter').val(); // Get multiple selected options
    const selectedGender = $('#genderFilter').val();       // Get multiple selected options
    const selectedVisitType = $('#visitTypeFilter').val(); // Get multiple selected options
    const fromDate = $('#fromDate').val();
    const toDate = $('#toDate').val();

    // Filter the patient data based on the selected filters
    const filteredData = patientData.filter(function(patient) {
        const patientDate = new Date(patient.date); // Ensure the patient date is a valid Date object
        const isInDateRange = (!fromDate || patientDate >= new Date(fromDate)) &&
                              (!toDate || patientDate <= new Date(toDate));

        // Handle multiple selection for Diagnosis, Gender, and Visit Type
        const matchesDiagnosis = !selectedDiagnosis.length || selectedDiagnosis.includes(patient.diagnosis);
        const matchesGender = !selectedGender.length || selectedGender.includes(patient.gender);
        const matchesVisitType = !selectedVisitType.length || selectedVisitType.includes(patient.visit_type);

        return matchesDiagnosis && matchesGender && matchesVisitType && isInDateRange;
    });

    // Clear the table and update with filtered data
    table.clear();
    filteredData.forEach(function(patient) {
        table.row.add([
            patient.patient_id,
            patient.date,
            patient.age,
            patient.gender,
            patient.diagnosis,
            patient.lab_results,
            patient.medication,
            patient.visit_type,
            patient.outcome
        ]).draw();
    });

    // Update the chart with the filtered data
    updateChart(filteredData);

    // Update metrics with the filtered data
    calculateMetrics(filteredData);
}

// Export data functionality to CSV
function exportData() {
    const table = $('#patientTable').DataTable();
    const data = table.rows().data().toArray(); // Get all the table data
    const csv = [];

    // Add table headers to CSV
    const headers = ['Patient ID', 'Date', 'Age', 'Gender', 'Diagnosis', 'Lab Results', 'Medication', 'Visit Type', 'Outcome'];
    csv.push(headers.join(','));

    // Add data rows to CSV
    data.forEach(function(row) {
        csv.push(row.join(','));
    });

    // Create CSV file
    const csvFile = new Blob([csv.join('\n')], { type: 'text/csv' });

    // Create a download link
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(csvFile);
    downloadLink.download = 'patient_data.csv';

    // Trigger the download
    downloadLink.click();
}