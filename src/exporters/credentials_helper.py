# credentials_helper.py
import os
import json
import logging

logging.basicConfig(level=logging.INFO)

def save_credentials(credentials_dict):
    # Potential directories to save credentials
    potential_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials'),
        os.path.join('D:\\cohesive\\cohesive', 'credentials'),
        os.path.join('D:\\cohesive\\cohesive\\src', 'credentials'),
        os.path.join(os.getcwd(), 'credentials')
    ]

    # Ensure credentials directory exists
    for directory in potential_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            
            # Attempt to save credentials
            credentials_path = os.path.join(directory, 'google_sheets_credentials.json')
            
            with open(credentials_path, 'w') as f:
                json.dump(credentials_dict, f, indent=2)
            
            logging.info(f"Credentials saved successfully to: {credentials_path}")
            return credentials_path
        
        except Exception as e:
            logging.warning(f"Could not save to {directory}: {e}")
    
    logging.error("Failed to save credentials to any directory")
    return None

def verify_credentials(credentials_dict):
    """Verify the credentials dictionary has all required fields"""
    required_keys = [
        'type', 'project_id', 'private_key', 
        'client_email', 'client_id'
    ]
    
    missing_keys = [key for key in required_keys if key not in credentials_dict]
    
    if missing_keys:
        logging.error(f"Missing keys: {missing_keys}")
        return False
    
    logging.info("Credentials appear to be valid!")
    return True

if __name__ == "__main__":
    # Your credentials dictionary
    credentials = {
        
    }

    # Verify credentials
    if verify_credentials(credentials):
        # Attempt to save credentials
        save_credentials(credentials)
