# credentials_diagnostics.py
import os
import sys
import json
import logging

logging.basicConfig(level=logging.DEBUG)

def print_directory_contents(path):
    """Print contents of a directory to help diagnose file location issues"""
    logging.info(f"Examining directory: {path}")
    try:
        if os.path.exists(path):
            contents = os.listdir(path)
            logging.info(f"Directory contents: {contents}")
        else:
            logging.warning(f"Directory does not exist: {path}")
    except Exception as e:
        logging.error(f"Error examining directory {path}: {e}")

def find_credentials():
    """Comprehensive credentials file search"""
    # Possible base directories to search
    base_directories = [
        os.getcwd(),  # Current working directory
        os.path.dirname(os.path.abspath(__file__)),  # Script's directory
        'D:\\cohesive',
        'D:\\cohesive\\cohesive',
        os.path.expanduser('~'),  # User home directory
    ]

    # Potential credential file names
    credential_filenames = [
        'google_sheets_credentials.json',
        'credentials.json',
        'sheets_credentials.json'
    ]

    found_credentials = []

    # Search through possible directories and filenames
    for base_dir in base_directories:
        logging.info(f"Searching in base directory: {base_dir}")
        
        # Print directory contents to help diagnose
        print_directory_contents(base_dir)
        
        for root, dirs, files in os.walk(base_dir):
            for filename in credential_filenames:
                potential_path = os.path.join(root, filename)
                
                if os.path.exists(potential_path):
                    logging.info(f"Found potential credentials file: {potential_path}")
                    
                    # Verify file contents
                    try:
                        with open(potential_path, 'r') as f:
                            credentials = json.load(f)
                        
                        # Check for essential keys
                        required_keys = ['type', 'project_id', 'private_key', 'client_email']
                        if all(key in credentials for key in required_keys):
                            found_credentials.append(potential_path)
                            logging.info(f"Valid credentials found at: {potential_path}")
                    except json.JSONDecodeError:
                        logging.warning(f"Invalid JSON in {potential_path}")
                    except Exception as e:
                        logging.error(f"Error reading {potential_path}: {e}")

    return found_credentials

def main():
    logging.info("Starting credentials diagnostic...")
    
    # Print current working directory and script location
    logging.info(f"Current Working Directory: {os.getcwd()}")
    logging.info(f"Script Location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Find credentials
    credentials_paths = find_credentials()
    
    if credentials_paths:
        logging.info("Credentials files found:")
        for path in credentials_paths:
            logging.info(path)
    else:
        logging.error("No valid credentials file found.")
        
        # Provide additional debugging information
        logging.info("Python Path:")
        for path in sys.path:
            logging.info(path)

if __name__ == "__main__":
    main()