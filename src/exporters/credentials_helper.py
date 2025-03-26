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
        "type": "service_account",
        "project_id": "lustrous-pivot-416108",
        "private_key_id": "3d2cbe77928f233da9d5f2383f12c16221a6c9ed",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDALyTJZTUeJRCz\nRN/x03qWS3MhGZPx/qVpiyEFOibZ7+BQbaZgMnUjcU/FfqlO88idf3U4OJAot8+g\n6ZYLTWgqE9EljZnxfoBtAdJrRbpXvx3JjTDYTZ4yiQu5fQC22pomUqsicC37+3vI\nmVKTiiJojKq5KYgM9MYaCvopmBqn0C4TF7iCj6etK9TUbEuvmGF6a01qZlQTfQZS\nSVYEFDsTa4E4JPJB/1QjoI5cIxG/3YtWkpFTxGXaB/Ibxq8G1JURcg+hwZ2bTndq\nnMD8GkhTKSKQe57Lb0joc1TGnDeMBVdt3H2hKck9TegX6RW57W4f5pOagE56RBts\nb+pkzZGfAgMBAAECggEAEQHbB+DnTiSfkWMYoluXBJ08B1jZHoLs0SXuenpGnTtn\nfBadW56mKR3KSRhIFA7qLliXigMkwXBgH8WsG+dHaY8uugZe8jUXWQ4z4ymyL45f\n13ShjEgfe39kmeSgXzjXMr8BcAnCDVjtqmHkdzQJOXwBUQ4w1lyu+fewuGTtLvPL\nwS5eMzJCuEdqCIv0WquHPjintyEkOEkFabd5DEXrYFYmrfRTDQimlJxs1hKRS6F/\nhkr/6vXBshQSahoVVcyg+VH4Nq1GuOKKOEiqVpHLUKEci+3r07ycnRCp7bdjjswV\nJn41i2yBivMIxJtfzvN9YMU4BaAk+RqKY/Sc+yZTGQKBgQDiUrSlhB18+oSnFeiA\nfRemdOcn85gWu2wIYEpoRIzArDxFPpDc2RFtfpgcfzskja448rBdT2LlOqXcU8Yt\nt+2R8EN861aWTYrwu4LZRV7qU6z3GewjnBQvbbJqoC0f1ALlNss0Ie8VOuqjJtFh\nsmI1YqJ0AGI9KwXrLAJgV5TXLQKBgQDZYnNf5+Y3PUcSM8goMDo6M4efHCmBtqYV\nFiMem7BHhvjHaPWauksZN9RHyi/ykomzL0oG6EcbXyO8qy+KIHQYXQn1A6gwid8b\n+Y53pT8WYioPjMHXbJp8B66NcDkJtA2DVLbMJ32T01aGcoVYM/Ng7NK8WghpkJef\n63yb0kBLewKBgCGUm/EjFS0CDsSr33+RD/1GwzWOUzasQG9NujyWTzwXUioECoJ6\nQre4XOF9j0zxKLSSbdCqgsX4WbvDQlhuPfW1bI4QbRyIDOGDMPsD6/1gxP00/3CZ\nK/WNlTd05L0gO/2+j5AAqPTBdScYD2Erkp7RL8F+fRUOWSZ3tTKOTCtRAoGATGqd\nYDNm7DgwSafGTspVTaxbmoUN2jlYvMThZ5sXJq29umudGt0uFRlZGDttC3qTyVdw\nUGlKxcZ2C5apyYaLCR17qJO2hgmRUoYxnMGMIdQ0MO8sHQxiagNRSwsOIekXbvlS\noQWo0VRTcEPFuDHa9lGJ6whDOMjJZEAlt6j7TQ0CgYACW6RsnPB1Jk6uhrWNwo3G\nAVelbmv67EDxoJSPr3ytwLxYuqpJ6wqzSMTSixm4+GHUgKujF5rOcMVVTaWhEEaP\nyEGZAndUEJs2uJK1irJ+U5UszA2yCj62pEglMmYvl6tDGuSrd20nZtw0Vkfze/uI\n7vCOUq0d1lYCxL2LZ5oltg==\n-----END PRIVATE KEY-----\n",
        "client_email": "lead-generator@lustrous-pivot-416108.iam.gserviceaccount.com",
        "client_id": "109096524552704931472"
    }

    # Verify credentials
    if verify_credentials(credentials):
        # Attempt to save credentials
        save_credentials(credentials)