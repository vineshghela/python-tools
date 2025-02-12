import boto3
import csv
from botocore.exceptions import ClientError
import os
from datetime import datetime
from collections import defaultdict

def read_id_entity_mappings(filename):
    """
    Read ID-Entity mappings from CSV file.
    Returns a dictionary with entity_id as key and list of ids as values.
    """
    mappings = defaultdict(list)
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entity_id = row['entity_id'].strip()
                id = row['id'].strip()
                mappings[entity_id].append(id)
        return mappings
    except Exception as e:
        print(f"Error reading ID-Entity mappings file: {str(e)}")
        return {}

def read_uuids(filename):
    """
    Read UUIDs from CSV file.
    """
    uuids = set()
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            # Skip header if present
            if 'uuid' in str(next(reader, [])).lower():
                pass
            else:
                file.seek(0)
            
            for row in reader:
                if row:  # Skip empty rows
                    uuid = row[0].strip()
                    uuids.add(uuid)
        return uuids
    except Exception as e:
        print(f"Error reading UUIDs file: {str(e)}")
        return set()

def create_folder_structure(s3_client, bucket_name, entity_id, id):
    """
    Create folder structure: entity_id/id/Drafts
    Returns True if successful, False otherwise.
    """
    try:
        # Create the ID folder inside entity_id folder
        id_folder = f"{entity_id}/{id}/"
        s3_client.put_object(Bucket=bucket_name, Key=id_folder)
        
        # Create the Drafts folder
        drafts_folder = f"{entity_id}/{id}/Drafts/"
        s3_client.put_object(Bucket=bucket_name, Key=drafts_folder)
        
        return True
    except ClientError as e:
        print(f"Error creating folders for entity_id: {entity_id}, id: {id}")
        print(f"Error: {str(e)}")
        return False

def process_folders(bucket_name, uuid_file, mapping_file):
    """
    Main processing function.
    """
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # Read input files
    print("Reading input files...")
    uuids = read_uuids(uuid_file)
    id_entity_mappings = read_id_entity_mappings(mapping_file)
    
    if not uuids or not id_entity_mappings:
        print("Error: Could not read input files.")
        return
    
    print(f"\nFound {len(uuids)} UUIDs")
    print(f"Found {len(id_entity_mappings)} entity IDs with mappings")
    
    # Track results
    successful = []
    failed = []
    
    # Process each UUID that matches an entity_id
    for entity_id in uuids:
        if entity_id in id_entity_mappings:
            print(f"\nProcessing entity_id: {entity_id}")
            print(f"Creating folders for {len(id_entity_mappings[entity_id])} IDs")
            
            for id in id_entity_mappings[entity_id]:
                if create_folder_structure(s3_client, bucket_name, entity_id, id):
                    successful.append((entity_id, id))
                    print(f"Created folders for ID: {id}")
                else:
                    failed.append((entity_id, id))
        else:
            print(f"No mappings found for UUID: {entity_id}")
    
    return successful, failed

def save_log(successful, failed):
    """
    Save results to a log file.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'folder_creation_log_{timestamp}.csv'
    
    try:
        with open(log_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Status', 'Entity ID', 'ID'])
            
            for entity_id, id in successful:
                writer.writerow(['SUCCESS', entity_id, id])
            for entity_id, id in failed:
                writer.writerow(['FAILED', entity_id, id])
                
        print(f"\nLog saved to: {log_file}")
    except Exception as e:
        print(f"Error saving log: {str(e)}")

if __name__ == "__main__":
    bucket_name = "london-codedlawdocumentstorage"
    uuid_file = "toDelete.csv"
    mapping_file = "id-entity-id.csv"
    
    print("Starting folder creation process...")
    
    # Confirm before proceeding
    confirm = input(f"\nCreate folder structure in {bucket_name}? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        exit(0)
    
    # Process folders
    successful, failed = process_folders(bucket_name, uuid_file, mapping_file)
    
    # Print summary
    print("\nSummary:")
    print(f"Successfully created: {len(successful)} folder structures")
    print(f"Failed: {len(failed)} folder structures")
    
    # Save log
    save_log(successful, failed)
    
    if failed:
        print("\nFailed creations:")
        for entity_id, id in failed:
            print(f"Entity ID: {entity_id}, ID: {id}")