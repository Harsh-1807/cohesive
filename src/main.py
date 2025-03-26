# src/main.py
import os
import sys
import logging
import openai
from datetime import datetime
import streamlit as st

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from src.scrapers.google_search_scraper import GoogleSearchScraper
from src.scrapers.linkedin_scraper import LinkedInProfileScraper
from src.generators.email_generator import EmailGenerator
from src.exporters.google_sheets_exporter import LeadExporter
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger('main_script', level=logging.DEBUG)

# Load environment variables
load_dotenv()

def enrich_business_description(initial_description, company_name):
    """
    Use OpenAI to generate a more detailed business description.
    """
    try:
        # Ensure OpenAI API key is set
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        openai_response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Provide a professional, concise description for {company_name}. Initial context: {initial_description}",
            max_tokens=150
        )
        return openai_response.choices[0].text.strip()
    except Exception as e:
        logger.error(f"AI Description Generation Error: {e}")
        return initial_description

def generate_leads(search_query, business_location, num_results):
    # Set export timestamp
    export_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.environ['EXPORT_TIMESTAMP'] = export_timestamp
    logger.info(f"Starting lead generation process at {export_timestamp}")

    # Initialize scrapers and generators
    google_scraper = GoogleSearchScraper()
    linkedin_scraper = LinkedInProfileScraper()
    email_generator = EmailGenerator()

    # Execute Google search with user parameters
    try:
        search_results = google_scraper.search(
            query=search_query, 
            business_type=f"in {business_location}", 
            num_results=num_results
        )
        logger.info(f"Found {len(search_results)} search results")
    except Exception as search_error:
        logger.error(f"Search scraping failed: {search_error}")
        search_results = []

    # Process each search result to build consolidated leads
    consolidated_leads = []
    for result in search_results:
        try:
            company_name = result.get('title', '')
            # Extract the domain from the URL
            try:
                company_domain = result.get('link', '').split('//')[1].split('/')[0]
            except IndexError:
                company_domain = ""
            
            logger.info(f"Processing company: {company_name}")
            
            # Enrich business description using OpenAI
            try:
                enriched_description = enrich_business_description(
                    result.get('snippet', ''), 
                    company_name
                )
            except Exception as description_error:
                logger.warning(f"Description enrichment failed: {description_error}")
                enriched_description = result.get('snippet', '')
            
            # Generate potential email formats
            potential_emails = email_generator.generate_email_formats(
                company_name=company_name, 
                domain=company_domain
            )
            
            # Advanced email verification
            validated_emails = []
            for email in potential_emails:
                try:
                    verification = email_generator.advanced_email_verification(email)
                    validated_email_entry = {
                        'email': email,
                        'valid_format': verification.get('format_valid', False),
                        'domain_valid': verification.get('domain_valid', False),
                        'verification_status': verification.get('status', 'Unknown'),
                        'verification_score': verification.get('score', 'N/A')
                    }
                    validated_emails.append(validated_email_entry)
                    logger.info(f"Email {email} verification: {validated_email_entry}")
                except Exception as email_verify_error:
                    logger.warning(f"Email verification failed for {email}: {email_verify_error}")
            
            # Find LinkedIn profiles for the company
            try:
                linkedin_profiles = linkedin_scraper.find_profiles(
                    company_name=company_name, 
                    location=business_location,
                    num_results=3
                )
                linkedin_urls = [p.get('profile_url', '') for p in linkedin_profiles]
            except Exception as linkedin_error:
                logger.warning(f"LinkedIn profile scraping failed for {company_name}: {linkedin_error}")
                linkedin_urls = []
            
            # Build the lead entry
            lead_entry = {
                'company_name': company_name,
                'website': result.get('link', ''),
                'description': enriched_description,
                'emails': validated_emails,
                'linkedin_profiles': linkedin_urls,
                'verification_status': 'Initial',
                'timestamp': export_timestamp
            }
            
            consolidated_leads.append(lead_entry)
        
        except Exception as company_process_error:
            logger.error(f"Error processing company {company_name}: {company_process_error}")
    
    # Export the consolidated leads to Google Sheets
    try:
        exporter = LeadExporter()
        spreadsheet_id = exporter.export_leads(consolidated_leads)
        share_email = os.getenv('SHARE_EMAIL')
        if share_email:
            exporter.share_spreadsheet(spreadsheet_id, share_email)
        logger.info(f"Leads exported to Google Sheets. Spreadsheet ID: {spreadsheet_id}")
    except Exception as export_error:
        logger.error(f"Export failed: {export_error}")
        spreadsheet_id = None

    return consolidated_leads, spreadsheet_id

def main():
    st.title("Lead Generation App")
    st.write("Enter your search parameters below to generate business leads.")
    
    # User inputs
    search_query = st.text_input("Search Query", "tech startups")
    business_location = st.text_input("Business Location", "San Francisco")
    num_results = st.number_input("Number of Results", min_value=1, max_value=50, value=5, step=1)
    
    if st.button("Generate Leads"):
        with st.spinner("Generating leads..."):
            leads, spreadsheet_id = generate_leads(search_query, business_location, num_results)
        st.success("Lead generation complete!")
        
        # Display results
        st.subheader("Consolidated Leads:")
        st.write(leads)
        
        if spreadsheet_id:
            st.write(f"Leads exported to Google Sheets. Spreadsheet ID: {spreadsheet_id}")
        else:
            st.write("Export to Google Sheets failed.")

if __name__ == "__main__":
    main()
