import boto3
import csv
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
import os

def get_s3_transaction_ids(bucket_name):
    """
    Get all transaction IDs from both first and second levels of the S3 bucket.
    """
    s3_client = boto3.client('s3')
    transaction_ids = set()
    
    try:
        # First, get all top-level folders
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Delimiter='/')
        
        print("\nScanning S3 bucket structure...")
        
        # Process first level
        for page in pages:
            if 'CommonPrefixes' in page:
                for prefix in page['CommonPrefixes']:
                    top_folder = prefix['Prefix'].rstrip('/')
                    try:
                        # Validate if it's a UUID
                        uuid_obj = uuid.UUID(top_folder)
                        transaction_ids.add(str(uuid_obj))
                        print(f"Found top-level transaction: {top_folder}")
                    except ValueError:
                        # If not a UUID, check its subfolders
                        sub_pages = paginator.paginate(
                            Bucket=bucket_name,
                            Prefix=prefix['Prefix'],
                            Delimiter='/'
                        )
                        for sub_page in sub_pages:
                            if 'CommonPrefixes' in sub_page:
                                for sub_prefix in sub_page['CommonPrefixes']:
                                    sub_folder = sub_prefix['Prefix'].rstrip('/')
                                    # Extract the last part of the path
                                    sub_id = sub_folder.split('/')[-1]
                                    try:
                                        uuid_obj = uuid.UUID(sub_id)
                                        transaction_ids.add(str(uuid_obj))
                                        print(f"Found second-level transaction: {sub_id}")
                                    except ValueError:
                                        continue
                    
        print(f"\nFound total of {len(transaction_ids)} unique transaction IDs in S3")
        return transaction_ids
    except ClientError as e:
        print(f"Error accessing S3 bucket: {str(e)}")
        return set()

def read_keep_ids(filename):
    """
    Read transaction IDs to keep from the CSV file.
    """
    keep_ids = set()
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found in current directory.")
        print(f"Current directory contents: {os.listdir('.')}")
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
                    try:
                        uuid_obj = uuid.UUID(trans_id)
                        keep_ids.add(str(uuid_obj))
                    except ValueError:
                        print(f"Invalid UUID in keep list: {trans_id}")
                        continue
        
        print(f"Found {len(keep_ids)} valid transaction IDs to keep")
        return keep_ids
    except Exception as e:
        print(f"Error processing keep list file: {str(e)}")
        return set()

def export_to_delete(to_delete):
    """
    Export the transaction IDs to be deleted to a file.
    """
    filename = 'toDelete.csv'
    
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['transaction_id'])  # Header
            for trans_id in sorted(to_delete):
                writer.writerow([trans_id])
        print(f"\nTransactions to delete exported to: {filename}")
        print(f"Total transactions marked for deletion: {len(to_delete)}")
    except Exception as e:
        print(f"Error saving to delete list: {str(e)}")

if __name__ == "__main__":
    bucket_name = "london-codedlawdocumentstorage"
    keep_file = 'someids.csv'
    
    print("Starting S3 cleanup checker...")
    
    # First, get all transaction IDs from S3 (both levels)
    s3_transactions = get_s3_transaction_ids(bucket_name)
    
    # Then, read the keep list
    print(f"\nReading keep list from {keep_file}...")
    keep_transactions = read_keep_ids(keep_file)
    
    # Find transactions that are in S3 but not in the keep list
    to_delete = s3_transactions - keep_transactions
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total transactions found in S3: {len(s3_transactions)}")
    print(f"Transactions to keep (from CSV): {len(keep_transactions)}")
    print(f"Transactions to delete: {len(to_delete)}")
    
    # Export results
    if to_delete:
        export_to_delete(to_delete)
        print("\nFirst 10 transactions to delete (preview):")
        for trans_id in sorted(list(to_delete)[:10]):
            print(trans_id)
        if len(to_delete) > 10:
            print(f"... and {len(to_delete) - 10} more")
    else:
        print("\nNo transactions to delete found.")