import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

def calculate_age(birth_date: str, reference_date: str) -> int:
    """Calculate age in years from birth_date to reference_date"""
    birth = datetime.fromisoformat(birth_date)
    ref = datetime.fromisoformat(reference_date[:10])  # Handle both YYYY-MM-DD and full ISO
    age = ref.year - birth.year
    # Adjust if birthday hasn't occurred yet this year
    if (ref.month, ref.day) < (birth.month, birth.day):
        age -= 1
    return age

def parse_date(date_str: str) -> datetime:
    """Parse ISO datetime string to datetime object"""
    # Handle both 'YYYY-MM-DD' and 'YYYY-MM-DDTHH:MM:SS+TZ' formats
    return datetime.fromisoformat(date_str[:19])

def extract_patient_info(filepath: Path) -> Dict:
  with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

    patient_id = None
    birth_date = None
    gender = None
    encounters = [] 
    conditions = [] 

    # Loop through all resources in the FHIR bundle
    for entry in data.get('entry', []):
        resource = entry.get('resource', {})
        resource_type = resource.get('resourceType')
        
        if resource_type == 'Patient':
            patient_id = resource.get('id')
            birth_date = resource.get('birthDate')
            gender = resource.get('gender')
        
        elif resource_type == 'Encounter':
            period = resource.get('period', {})
            start = period.get('start')
            end = period.get('end')
            encounter_class = resource.get('class', {}).get('code', 'unknown')
            
            if start:
                encounters.append({
                    'start': start,
                    'end': end,
                    'type': encounter_class
                })
        
        elif resource_type == 'Condition':
            condition_code = resource.get('code', {}).get('text', 'Unknown')
            onset = resource.get('onsetDateTime')
            
            if onset:
                conditions.append({
                    'name': condition_code,
                    'onset': onset
                })
    
    return {
        'patient_id': patient_id,
        'birth_date': birth_date,
        'gender': gender,
        'encounters': encounters,
        'conditions': conditions
    }


def calculate_readmission_labels(encounters: List[Dict]) -> List[Dict]:
  inpatient = [e for e in encounters if e['type'] in ['IMP', 'EMER', 'inpatient', 'emergency']] 
  inpatient.sort(key=lambda x:x['start']) #lambda -> one use function

  discharge_events = [] 

  for i, encounter in enumerate(inpatient):
    #get discharge dates 
    if encounter['end']:
      discharge_date = parse_date(encounter['end'])
    else:
      discharge_date = parse_date(encounter['start'])
    
    is_readmitted = False 
    for future_encounter in inpatient[i+1:]:
      future_start = parse_date(future_encounter['start'])
      days_diff = (future_start - discharge_date).days

      if 0 < days_diff <= 30:
        is_readmitted = True 
        break 
    
    discharge_events.append({
            'discharge_date': discharge_date.isoformat(),
            'encounter_type': encounter['type'],
            'is_readmitted_30_days': is_readmitted
        })

  return discharge_events 