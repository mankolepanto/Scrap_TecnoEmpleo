import csv
import os
from collections import OrderedDict

def update_csv_with_job_data(job_data, filename='job_data.csv'):
    # Get all unique keys from all jobs
    all_keys = set()
    for job in job_data:
        all_keys.update(job.keys())
        all_keys.update(job['details'].keys())
        all_keys.update(job['additional_info'].keys())
        for text in job['additional_info'].get('textos_limpios', []):
            if ':' in text:
                key, _ = text.split(':', 1)
                all_keys.add(key.strip())
    
    # Define columns
    columns = ['offer_id'] + list(all_keys)  # Ensure offer_id is the first column
    columns.extend(['textos_limpios', 'tecnologias'])
    
    # Check if file exists and get existing job IDs
    file_exists = os.path.isfile(filename)
    existing_ids = set()
    if file_exists:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_ids = {row['offer_id'] for row in reader if 'offer_id' in row}
    
    # Open file in append mode if it exists, or write mode if it doesn't
    mode = 'a' if file_exists else 'w'

    rows_added = 0
    
    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        
        # Write header only if the file is new
        if not file_exists:
            writer.writeheader()
        
        for job in job_data:
            # Skip if job already exists in the CSV
            if job['offer_id'] in existing_ids:
                continue
            
            row = OrderedDict.fromkeys(columns)  # Initialize all columns with None
            row.update(job)  # Copy all job data
            
            # Handle details and additional info
            row.update(job['details'])
            row.update(job['additional_info'])
            
            # Handle technologies
            row['tecnologias'] = ', '.join(job['additional_info'].get('tecnologias', []))
            
            # Handle clean texts
            textos_limpios = []
            for text in job['additional_info'].get('textos_limpios', []):
                if ':' in text:
                    key, value = text.split(':', 1)
                    row[key.strip()] = value.strip()
                else:
                    textos_limpios.append(text)
            row['textos_limpios'] = ', '.join(textos_limpios)
            
            # Remove nested dictionaries to avoid errors
            row.pop('details', None)
            row.pop('additional_info', None)
            
            writer.writerow(row)
            rows_added += 1
    
    print(f"CSV file '{filename}' has been updated successfully.")
    print(f"Number of new rows added: {rows_added}")
    return rows_added  # Return the number of added rows