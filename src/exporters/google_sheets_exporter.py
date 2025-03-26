# src/exporters/google_sheets_exporter.py
import os
import logging
from datetime import datetime
from typing import List, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build

class LeadExporter:
    def __init__(self, credentials_filename='google_sheets_credentials.json'):
        # Enhanced path resolution strategies
        possible_paths = [
            # Explicit full paths for your specific system
            r'D:\cohesive\cohesive\src\credentials\google_sheets_credentials.json',
            r'D:\cohesive\cohesive\credentials\google_sheets_credentials.json',
            
            # Current project structure
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials', credentials_filename),
            
            # Alternative path
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'credentials', credentials_filename),
            
            # Absolute path fallback
            os.path.join(os.path.expanduser('~'), 'cohesive', 'credentials', credentials_filename),
            
            # Relative to current working directory
            os.path.join(os.getcwd(), 'credentials', credentials_filename)
        ]

        # Find the first existing credentials file
        credentials_path = next((path for path in possible_paths if os.path.exists(path)), None)

        if not credentials_path:
            error_msg = f"Google Sheets credentials not found. Checked paths:\n" + "\n".join(possible_paths)
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)

        logging.info(f"Using credentials from: {credentials_path}")

        try:
            # Use service account credentials
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path, 
                scopes=['https://www.googleapis.com/auth/spreadsheets', 
                        'https://www.googleapis.com/auth/drive']  # Added drive scope for sharing
            )
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        except Exception as e:
            logging.error(f"Failed to initialize Google Sheets service: {e}")
            raise

    def export_leads(self, leads: List[Dict], share_email: str = None) -> str:
        """
        Export leads to a new Google Sheets spreadsheet
        
        :param leads: List of lead dictionaries
        :param share_email: Optional email to share the spreadsheet with
        :return: Spreadsheet ID
        """
        try:
            # Create a new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': f'Lead Export - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                }
            }
            spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet, 
                fields='spreadsheetId'
            ).execute()
            spreadsheet_id = spreadsheet['spreadsheetId']

            # Prepare headers and data
            headers = [
                'Company Name', 'Website', 'Description', 
                'Emails', 'LinkedIn Profiles', 'Verification Status'
            ]
            
            # Transform leads into rows
            rows = []
            for lead in leads:
                row = [
                    lead.get('company_name', ''),
                    lead.get('website', ''),
                    lead.get('description', ''),
                    ', '.join([e['email'] for e in lead.get('emails', [])]),
                    ', '.join(lead.get('linkedin_profiles', [])),
                    lead.get('verification_status', '')
                ]
                rows.append(row)

            # Combine headers and data
            values = [headers] + rows

            # Write data to the sheet
            body = {'values': values}
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, 
                range='Sheet1!A1', 
                valueInputOption='RAW', 
                body=body
            ).execute()

            # Optional sharing
            if share_email:
                self.share_spreadsheet(spreadsheet_id, share_email)

            return spreadsheet_id

        except Exception as e:
            logging.error(f"Failed to export leads: {e}")
            raise

    def share_spreadsheet(self, spreadsheet_id: str, email: str):
        """
        Share the spreadsheet with a specific email
        
        :param spreadsheet_id: ID of the spreadsheet to share
        :param email: Email to share with
        """
        try:
            # Drive API for sharing
            drive_service = build('drive', 'v3', credentials=self.credentials)
            
            # Define permission
            permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': email
            }
            
            # Execute sharing
            drive_service.permissions().create(
                fileId=spreadsheet_id, 
                body=permission
            ).execute()
            
            logging.info(f"Spreadsheet {spreadsheet_id} shared with {email}")
        
        except Exception as e:
            logging.error(f"Failed to share spreadsheet: {e}")
            raise