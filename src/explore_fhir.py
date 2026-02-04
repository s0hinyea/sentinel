import json 
from pathlib import Path 
from collections import Counter

def parse_patient_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
      data = json.load(f)

      birth_date = None 
      encounters = [] 

      # FHIR bundles have an "entry" array with all resources

      for entry in data.get('entry', []):
        resource = entry.get('resource', {})
        resource_type = resource.get('resourceType')

        if resource_type == 'Patient':
          birth_date = resource.get('birthDate')

        elif resource_type == 'Encounter':
            period = resource.get('period', {})
            start = period.get('start')
            if start:
                encounters.append(start)
    
    return {
        'birth_date': birth_date,
        'encounters': encounters
    }

def main():

  fhir_dir = Path("../output/fhir")

  patient_files = list(fhir_dir.glob('*.json'))
  print(f"Found {len(patient_files)} patient files\n")

  first = parse_patient_file(patient_files[0])
  print(f"Example Patient Birth: {first['birth_date']}")
  print(f"Encounters: {len(first['encounters'])}")
    
  if first['encounters']:
    print(f"First Encounter: {min(first['encounters'])}")
    print(f"Last Encounter: {max(first['encounters'])}")
    
  print("\n" + "="*50)
  print("Year Distribution (50 patient sample)")
  print("="*50 + "\n")
  
    # Collect encounter years from 50 patients
  years = []
  for pfile in patient_files[:50]:
      patient = parse_patient_file(pfile)
      for enc in patient['encounters']:
          year = enc[:4]  # Extract "YYYY" from "YYYY-MM-DD"
          years.append(year)
    
    # Count how many encounters per year
  year_counts = Counter(years)
  for year in sorted(year_counts.keys()):
      print(f"{year}: {year_counts[year]} encounters")

if __name__ == "__main__":
    main()