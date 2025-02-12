import boto3
from collections import defaultdict
import json
from datetime import datetime

def get_two_level_folder_structure(bucket_name):
    """
    Get folder structure up to 2 levels deep from an S3 bucket.
    Returns a dictionary of the structure.
    Excludes the 'templates' folder.
    """
    s3_client = boto3.client('s3')
    
    # Structure to hold our folder hierarchy
    folder_structure = defaultdict(list)
    
    try:
        # List all objects to get both files and folders
        paginator = s3_client.get_paginator('list_objects_v2')
        
        # First, get all top-level prefixes
        for page in paginator.paginate(Bucket=bucket_name, Delimiter='/'):
            if 'CommonPrefixes' in page:
                for prefix in page['CommonPrefixes']:
                    top_folder = prefix['Prefix'].rstrip('/')
                    # Skip the templates folder
                    if top_folder and top_folder != 'templates':
                        folder_structure[top_folder] = []
        
        # Then, for each top-level folder, get its subfolders
        for top_folder in folder_structure.keys():
            prefix = f"{top_folder}/"
            for sub_page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter='/'):
                if 'CommonPrefixes' in sub_page:
                    for sub_prefix in sub_page['CommonPrefixes']:
                        sub_path = sub_prefix['Prefix']
                        # Extract just the subfolder name
                        sub_folder = sub_path.replace(prefix, '').rstrip('/')
                        if sub_folder:  # Ensure it's not empty
                            folder_structure[top_folder].append(sub_folder)
        
        # Sort the subfolders for each top-level folder
        for top_folder in folder_structure:
            folder_structure[top_folder].sort()
        
        # Convert defaultdict to regular dict and sort top-level folders
        return dict(sorted(folder_structure.items()))
        
    except Exception as e:
        print(f"Error accessing bucket {bucket_name}: {str(e)}")
        return {}

def export_to_json(data, filename=None):
    """
    Export the folder structure to a JSON file.
    If no filename is provided, creates one with timestamp.
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'folder_structure_{timestamp}.json'
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully exported to {filename}")
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {str(e)}")
        return False

if __name__ == "__main__":
    bucket_name = "london-codedlawdocumentstorage"
    
    # Get the folder structure
    folder_structure = get_two_level_folder_structure(bucket_name)
    
    # Export to JSON file
    export_to_json(folder_structure)
    
    # Also print to console
    print("Folder structure:")
    print(json.dumps(folder_structure, indent=2))