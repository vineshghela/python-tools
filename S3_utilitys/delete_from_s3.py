import boto3
import csv
from botocore.exceptions import ClientError
import time
from datetime import datetime
import os

def read_delete_list(filename):
    """
    Read the list of transaction IDs to delete from CSV.
    """
    delete_ids = set()
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found in current directory.")
        return set()
    
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
                    trans_id = row[0].strip()
                    delete_ids.add(trans_id)
        
        return delete_ids
    except Exception as e:
        print(f"Error reading delete list: {str(e)}")
        return set()

def delete_s3_directory(s3_client, bucket_name, directory):
    """
    Delete all objects in the specified S3 directory.
    """
    try:
        # List all objects in the directory
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=directory)
        
        delete_count = 0
        for page in pages:
            if 'Contents' in page:
                # Prepare objects for deletion
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                
                # Delete objects in batches of 1000 (S3 limit)
                for i in range(0, len(objects_to_delete), 1000):
                    batch = objects_to_delete[i:i + 1000]
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': batch}
                    )
                    delete_count += len(batch)
        
        return delete_count
    except ClientError as e:
        print(f"Error deleting directory {directory}: {str(e)}")
        return 0

def log_deletion(log_file, transaction_id, success, error_message=None):
    """
    Log the deletion operation to a file.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "SUCCESS" if success else "FAILED"
    error_info = f", Error: {error_message}" if error_message else ""
    
    with open(log_file, 'a') as f:
        f.write(f"{timestamp}, {transaction_id}, {status}{error_info}\n")

if __name__ == "__main__":
    bucket_name = "london-codedlawdocumentstorage"
    delete_file = "toDelete.csv"
    log_file = f"deletion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Create log file with header
    with open(log_file, 'w') as f:
        f.write("Timestamp, Transaction ID, Status, Error Message\n")
    
    print("Starting S3 directory deletion process...")
    
    # Read the list of directories to delete
    delete_ids = read_delete_list(delete_file)
    if not delete_ids:
        print("No directories to delete found in the file.")
        exit(1)
    
    print(f"\nFound {len(delete_ids)} directories to delete")
    
    # Confirm before proceeding
    confirm = input(f"\nAre you sure you want to delete {len(delete_ids)} directories? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        exit(0)
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # Process deletions
    total_deleted = 0
    total_failed = 0
    
    print("\nStarting deletion process...")
    start_time = time.time()
    
    for i, trans_id in enumerate(sorted(delete_ids), 1):
        try:
            # Add trailing slash to ensure we're working with the directory
            directory = f"{trans_id}/"
            
            # Delete the directory and its contents
            deleted_count = delete_s3_directory(s3_client, bucket_name, directory)
            
            if deleted_count > 0:
                print(f"Successfully deleted directory {trans_id} ({deleted_count} objects)")
                log_deletion(log_file, trans_id, True)
                total_deleted += 1
            else:
                print(f"No objects found in directory {trans_id}")
                log_deletion(log_file, trans_id, False, "No objects found")
                total_failed += 1
                
        except Exception as e:
            print(f"Error processing directory {trans_id}: {str(e)}")
            log_deletion(log_file, trans_id, False, str(e))
            total_failed += 1
        
        # Print progress
        if i % 10 == 0 or i == len(delete_ids):
            print(f"Progress: {i}/{len(delete_ids)} directories processed")
            
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print(f"\nDeletion process completed in {duration:.2f} seconds")
    print(f"Total directories successfully deleted: {total_deleted}")
    print(f"Total directories failed: {total_failed}")
    print(f"Detailed log saved to: {log_file}")