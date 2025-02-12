import boto3
import csv
from botocore.exceptions import ClientError
import os
from datetime import datetime

def read_uuids(filename):
    """
    Read UUIDs from CSV file.
    """
    uuids = []
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            # Skip header if present
            if 'transaction_id' in str(next(reader, [])).lower():
                pass
            else:
                file.seek(0)
            
            for row in reader:
                if row:  # Skip empty rows
                    uuid = row[0].strip()
                    uuids.append(uuid)
        return uuids
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return []

def create_empty_folders(bucket_name, uuids):
    """
    Create empty folders in S3 for each UUID.
    Returns lists of successful and failed creations.
    """
    s3_client = boto3.client('s3')
    successful = []
    failed = []
    
    print(f"\nCreating empty folders in bucket: {bucket_name}")
    
    for i, uuid in enumerate(uuids, 1):
        try:
            # Create empty folder by putting an empty object with trailing slash
            key = f"{uuid}/"
            s3_client.put_object(Bucket=bucket_name, Key=key)
            successful.append(uuid)
            print(f"Created folder: {uuid} ({i}/{len(uuids)})")
            
        except ClientError as e:
            print(f"Failed to create folder for {uuid}: {str(e)}")
            failed.append(uuid)
            
        # Print progress every 10 folders
        if i % 10 == 0:
            print(f"Progress: {i}/{len(uuids)} folders processed")
    
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
            writer.writerow(['Status', 'UUID'])
            
            for uuid in successful:
                writer.writerow(['SUCCESS', uuid])
            for uuid in failed:
                writer.writerow(['FAILED', uuid])
                
        print(f"\nLog saved to: {log_file}")
    except Exception as e:
        print(f"Error saving log: {str(e)}")

if __name__ == "__main__":
    bucket_name = "london-codedlawdocumentstorage"
    input_file = "toDelete.csv"  # Change this to your input file name
    
    print("Starting folder creation process...")
    
    # Read UUIDs from file
    uuids = read_uuids(input_file)
    if not uuids:
        print("No UUIDs found in input file.")
        exit(1)
    
    print(f"Found {len(uuids)} UUIDs to process")
    
    # Confirm before proceeding
    confirm = input(f"\nCreate {len(uuids)} empty folders in {bucket_name}? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        exit(0)
    
    # Create folders
    successful, failed = create_empty_folders(bucket_name, uuids)
    
    # Print summary
    print("\nSummary:")
    print(f"Total UUIDs processed: {len(uuids)}")
    print(f"Successfully created: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    # Save log
    save_log(successful, failed)
    
    if failed:
        print("\nFailed UUIDs:")
        for uuid in failed:
            print(uuid)