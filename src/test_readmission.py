from pathlib import Path
from extract_features import extract_patient_info, calculate_readmission_labels

# Test on one patient
fhir_dir = Path('../output/fhir')
patient_files = list(fhir_dir.glob('*.json'))

# Get the first patient
patient_data = extract_patient_info(patient_files[153])
print(f"Patient ID: {patient_data['patient_id']}")
print(f"Birth Date: {patient_data['birth_date']}")
print(f"Total Encounters: {len(patient_data['encounters'])}\n")

# Calculate readmissions
discharges = calculate_readmission_labels(patient_data['encounters'])
print(f"Total Discharge Events: {len(discharges)}\n")

# Show first 3 discharge events
for i, discharge in enumerate(discharges[:3]):
    print(f"Discharge {i+1}:")
    print(f"  Date: {discharge['discharge_date']}")
    print(f"  Type: {discharge['encounter_type']}")
    print(f"  Readmitted: {discharge['is_readmitted_30_days']}")
    print()